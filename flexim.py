#!/usr/bin/env python

"""
Recurring Read of a Flexim Unit

Based on BACpypes with AWS connector

IP addresses - site dependent
"""
import logging
import time
import os
import boto3
from dotenv import load_dotenv
from botocore.config import Config
from collections import deque
from bacpypes.debugging import bacpypes_debugging, ModuleLogger
from bacpypes.consolelogging import ConfigArgumentParser
from bacpypes.core import run, deferred
from bacpypes.iocb import IOCB
from bacpypes.task import RecurringTask
from bacpypes.pdu import Address
from bacpypes.object import get_datatype
from bacpypes.apdu import ReadPropertyRequest
from bacpypes.primitivedata import Unsigned, ObjectIdentifier
from bacpypes.constructeddata import Array
from bacpypes.app import BIPSimpleApplication
from bacpypes.local.device import LocalDeviceObject
load_dotenv()

# some debugging
_debug = 0
_log = ModuleLogger(globals())

# create a new boto3 session with timestream
session = boto3.Session()
client = session.client('timestream-write',region_name="us-east-2",aws_access_key_id=os.getenv("ACCESS_KEY"),aws_secret_access_key=os.getenv("SECRET_KEY"),config=Config(read_timeout=20, max_pool_connections=5000,retries={'max_attempts': 10}))
# the IP addresses of the targets - local IP is stored within BACpypes.ini file
ip_addresses = []
ip_addresses.extend(os.getenv("IP_ADDRESSES").split(","))
# the BACnet addresses of the targets
bacnet_addresses = []
bacnet_addresses.extend(os.getenv("BACNET_ADDRESSES").split(","))
#is each target dual or single channel
device_types = []
device_types.extend(os.getenv("DEVICE_TYPES").split(","))

# point list
point_list = []

for x in range(len(ip_addresses)):
    point_list.extend([
    #ChA Signal Amplitude
    (ip_addresses[x], 'analogInput:105', 'presentValue', bacnet_addresses[x]),
    #ChA Sound Speed
    (ip_addresses[x], 'analogInput:106', 'presentValue', bacnet_addresses[x]),
    #ChA Flow Rate & Diagnostics
    (ip_addresses[x], 'analogInput:111', 'presentValue', bacnet_addresses[x]),
    (ip_addresses[x], 'analogInput:111', 'eventState', bacnet_addresses[x]),
    (ip_addresses[x], 'analogInput:111', 'reliability', bacnet_addresses[x]),
    (ip_addresses[x], 'analogInput:111', 'outOfService', bacnet_addresses[x]),
    #ChA SNR
    (ip_addresses[x], 'analogInput:121', 'presentValue', bacnet_addresses[x]),
    #ChA SCNR
    (ip_addresses[x], 'analogInput:122', 'presentValue', bacnet_addresses[x])
    ])
    if device_types[x] == "dual":
        point_list.extend([
        #ChB Signal Amplitude
        (ip_addresses[x], 'analogInput:205', 'presentValue', bacnet_addresses[x]),
        #ChB Sound Speed
        (ip_addresses[x], 'analogInput:206', 'presentValue', bacnet_addresses[x]),
        #ChB Flow Rate & Diagnostics
        (ip_addresses[x], 'analogInput:211', 'presentValue', bacnet_addresses[x]),
        (ip_addresses[x], 'analogInput:211', 'eventState', bacnet_addresses[x]),
        (ip_addresses[x], 'analogInput:211', 'reliability', bacnet_addresses[x]),
        (ip_addresses[x], 'analogInput:211', 'outOfService', bacnet_addresses[x]),
        #ChB SNR
        (ip_addresses[x], 'analogInput:221', 'presentValue', bacnet_addresses[x]),
        #ChB SCNR
        (ip_addresses[x], 'analogInput:222', 'presentValue', bacnet_addresses[x])
        ])
    
#
#   PrairieDog
#
@bacpypes_debugging
class PrairieDog(BIPSimpleApplication, RecurringTask):

    def __init__(self, interval, *args):
        if _debug: PrairieDog._debug("__init__ %r %r", interval, args)
        BIPSimpleApplication.__init__(self, *args)
        RecurringTask.__init__(self, interval * 1000)

        # no longer busy
        self.is_busy = False

        # install the task
        self.install_task()

        # boolean allowing two batches per AWS transmission, if you want to batch
        # AWS use a 1KB write size so this is worth doing if ingestion is less than 500B
        #self.batchToggle = False

        #array to store Records
        self.records = []

    def process_task(self):
        if _debug: PrairieDog._debug("process_task")
        global point_list

        # check to see if we're idle
        if self.is_busy:
            if _debug: PrairieDog._debug("    - busy")
            return

        # now we are busy
        self.is_busy = True

        # turn the point list into a queue
        self.point_queue = deque(point_list)

        # clean out the list of the response values
        self.response_values = []

        # fire off the next request
        self.next_request()

    def next_request(self):
        if _debug: PrairieDog._debug("next_request")

        # check to see if we're done
        if not self.point_queue:
            if _debug: PrairieDog._debug("    - done")

            #if self.batchToggle == False:
                #print("records reset")
            self.records = []

            currentTime = str(int(round(time.time()*1000)))

            # dump out the results
            for request, response in zip(point_list, self.response_values):
                valueType = ""
                if (request[2]=="presentValue") or (request[2]=="covIncrement"):
                    valueType = "DOUBLE"
                else:
                    valueType = "VARCHAR"
                self.records.append({
                    'Time': currentTime,
                    'Dimensions': [{'Name': 'tag', 'Value': request[3]},
                                   {'Name': 'BACnet_ref', 'Value': request[1]}],
                    'MeasureName': request[2],
                    'MeasureValue': str(response),
                    'MeasureValueType': valueType,
                    })

            # for batching applications only
            #self.batchToggle = not self.batchToggle
            #if self.batchToggle == False:
            
            # replace with correct database and table names
            try:
                result = client.write_records(DatabaseName=os.getenv("DATABASE"), TableName=os.getenv("TABLE"), Records=self.records)
                #print("WriteRecords Status: [%s]" % result['ResponseMetadata']['HTTPStatusCode'])
            except client.exceptions.RejectedRecordsException as err:
                _print_rejected_recrods_Exceptions(err)
            except Exception as err:
                print("Error:",err)

            # no longer busy
            self.is_busy = False

            return

        # get the next request
        addr, obj_id, prop_id, bacnet_ref = self.point_queue.popleft()
        obj_id = ObjectIdentifier(obj_id).value

        # build a request
        request = ReadPropertyRequest(
            objectIdentifier=obj_id,
            propertyIdentifier=prop_id,
            )
        request.pduDestination = Address(addr)
        if _debug: PrairieDog._debug("    - request: %r", request)

        # make an IOCB
        iocb = IOCB(request)
        if _debug: PrairieDog._debug("    - iocb: %r", iocb)

        # set a callback for the response
        iocb.add_callback(self.complete_request)

        # give it to the application
        self.request_io(iocb)

    def complete_request(self, iocb):
        if _debug: PrairieDog._debug("complete_request %r", iocb)

        if iocb.ioResponse:
            apdu = iocb.ioResponse

            # find the datatype
            datatype = get_datatype(apdu.objectIdentifier[0], apdu.propertyIdentifier)
            if _debug: PrairieDog._debug("    - datatype: %r", datatype)
            if not datatype:
                raise TypeError("unknown datatype")

            # special case for array parts, others are managed by cast_out
            if issubclass(datatype, Array) and (apdu.propertyArrayIndex is not None):
                if apdu.propertyArrayIndex == 0:
                    value = apdu.propertyValue.cast_out(Unsigned)
                else:
                    value = apdu.propertyValue.cast_out(datatype.subtype)
            else:
                value = apdu.propertyValue.cast_out(datatype)
            if _debug: PrairieDog._debug("    - value: %r", value)

            # save the value
            self.response_values.append(value)

        if iocb.ioError:
            if _debug: PrairieDog._debug("    - error: %r", iocb.ioError)
            self.response_values.append(iocb.ioError)

        # fire off another request
        deferred(self.next_request)


def _print_rejected_recrods_Exceptions(err):
    print("RejectedRecords: ",err)
    for rr in err.response["RejectedRecords"]:
        print("Rejected Index " + str(rr["RecordIndex"]) + ": " + rr["Reason"])
        if "ExistingVersion" in rr:
            print("Rejected record existing version: ", rr["ExistingVersion"])

#
#   __main__
#
def main():
    # wait for a bit so that the IT connection is established on boot
    time.sleep(60)

    logging.basicConfig()
    # parse the command line arguments
    parser = ConfigArgumentParser(description=__doc__)

    # add an argument for interval
    parser.add_argument('interval', type=int,
          help='repeat rate in seconds',
          )

    # now parse the arguments
    args = parser.parse_args()

    if _debug: _log.debug("initialization")
    if _debug: _log.debug("    - args: %r", args)

    # make a device object
    this_device = LocalDeviceObject(ini=args.ini)
    if _debug: _log.debug("    - this_device: %r", this_device)


    # reboot the system on all uncaught exceptions to ensure best attempt at logging
    try:
        os.system("timeout 60 /etc/init.d/ntp stop")
        print("ntp stopped")
        time.sleep(10)
        os.system("timeout 60 ntpd -q -g")
        print("ntp synchronizing")
        time.sleep(10)
        os.system("timeout 60 /etc/init.d/ntp start")
        print("ntp restarted")
        # make a dog
        this_application = PrairieDog(args.interval, this_device, args.ini.address)
        if _debug: _log.debug("    - this_application: %r", this_application)
        _log.debug("running")
        run()
    except:
        print("could not initialise the application - is the network configured correctly?")
        time.sleep(1)
        print("hard rebooting in 10 seconds")
        time.sleep(10)
        os.system("reboot")

    _log.debug("fini")

if __name__ == "__main__":
    main()
