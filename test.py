#!/usr/bin/env python

"""
Test the AWS connection
"""

import logging
import time
import boto3
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

# some debugging
_debug = 0
_log = ModuleLogger(globals())

session = boto3.Session()
client = session.client('timestream-write', config=Config(read_timeout=20, max_pool_connections=5000,retries={'max_attempts': 10}))

ip_address = '172.23.99.14'

# point list
point_list = [
    #ChA Signal Amplitude
    (ip_address, 'analogInput:105', 'presentValue'),
    #ChA Sound Speed
    (ip_address, 'analogInput:106', 'presentValue'),
    #ChA Flow Rate & Diagnostics
    (ip_address, 'analogInput:108', 'presentValue'),
    (ip_address, 'analogInput:108', 'eventState'),
    (ip_address, 'analogInput:108', 'reliability'),
    (ip_address, 'analogInput:108', 'outOfService'),
    #ChA SNR
    (ip_address, 'analogInput:121', 'presentValue'),
    #ChA SCNR
    (ip_address, 'analogInput:122', 'presentValue'),
    #ChB Signal Amplitude
    (ip_address, 'analogInput:205', 'presentValue'),
    #ChB Sound Speed
    (ip_address, 'analogInput:206', 'presentValue'),
    #ChB Flow Rate & Diagnostics
    (ip_address, 'analogInput:208', 'presentValue'),
    (ip_address, 'analogInput:208', 'eventState'),
    (ip_address, 'analogInput:208', 'reliability'),
    (ip_address, 'analogInput:208', 'outOfService'),
    #ChB SNR
    (ip_address, 'analogInput:221', 'presentValue'),
    #ChB SCNR
    (ip_address, 'analogInput:222', 'presentValue')
    ]
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

        #boolean allowing two batches per AWS transmission
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
                    'Dimensions': [{'Name': 'tag', 'Value': '457000'},
                                   {'Name': 'BACnet_ref', 'Value': request[1]}],
                    'MeasureName': request[2],
                    'MeasureValue': str(response),
                    'MeasureValueType': valueType,
                    })

            #print(self.records)

            #print on every second fetch from instrument
            #self.batchToggle = not self.batchToggle
            #print("toggle set to: "+ str(self.batchToggle))

            #if self.batchToggle == False:
            try:
                result = client.write_records(DatabaseName="ScottishNHS",TableName="FleximTest",Records=self.records)
                #print("WriteRecords Status: [%s]" % result['ResponseMetadata']['HTTPStatusCode'])
            except client.exceptions.RejectedRecordsException as err:
                print(err)
            except Exception as err:
                print("Error:",err)

            # no longer busy
            self.is_busy = False

            return

        # get the next request
        addr, obj_id, prop_id = self.point_queue.popleft()
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
    records = []

    currentTime = str(int(round(time.time()*1000)))

    # dump out the results
    records.append({
        'Time': currentTime,
        'Dimensions': [{'Name': 'tag', 'Value': 'test'},
                    {'Name': 'BACnet_ref', 'Value': 'test'}],
        'MeasureName': 'test',
        'MeasureValue': 'test',
        'MeasureValueType': 'VARCHAR',
        })

    #print(self.records)

    #print on every second fetch from instrument
    #self.batchToggle = not self.batchToggle
    #print("toggle set to: "+ str(self.batchToggle))

    #if self.batchToggle == False:
    try:
        result = client.write_records(DatabaseName="ScottishNHS",TableName="inverclydeRoyal",Records=records)
        print("WriteRecords Status: [%s]" % result['ResponseMetadata']['HTTPStatusCode'])
    except client.exceptions.RejectedRecordsException as err:
        _print_rejected_recrods_Exceptions(err)
    except Exception as err:
        print("Error:",err)


if __name__ == "__main__":
    main()
