#!/usr/bin/python

"""
This sample application is a server that supports many core services that
applications need to present data on a BACnet network.  It supports Who-Is
and I-Am for device binding, Read and Write Property, Read and Write
Property Multiple, and COV subscriptions.
"""

from bacpypes.consolelogging import ConfigArgumentParser

from bacpypes.core import run

from bacpypes.app import BIPSimpleApplication
from bacpypes.object import AnalogValueObject, AnalogInputObject
from bacpypes.local.device import LocalDeviceObject
from bacpypes.service.cov import ChangeOfValueServices
from bacpypes.service.object import ReadWritePropertyMultipleServices


# globals
test_application = None

objectList = [
    AnalogInputObject(
        objectIdentifier=("analogInput", 101),
        objectName="chA medium temperature - supply line",
        presentValue=0.0,
        units="degreesCelsius",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 102),
        objectName="chA medium temperature - return line",
        presentValue=0.0,
        units="degreesCelsius",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 103),
        objectName="chA medium pressure - supply line",
        presentValue=0.0,
        units="bars",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 104),
        objectName="chA medium pressure - return line",
        presentValue=0.0,
        units="bars",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 105),
        objectName="chA signal amplitude",
        presentValue=0.0,
        units="noUnits",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 106),
        objectName="chA sound speed",
        presentValue=0.0,
        units="metersPerSecond",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 107),
        objectName="chA flow velocity",
        presentValue=0.0,
        units="metersPerSecond",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 108),
        objectName="chA volumetric flow rate",
        presentValue=0.0,
        units="cubicMetersPerHour",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogValueObject(
        objectIdentifier=("analogValue", 109),
        objectName="chA volumetric flow rate, + totalizer",
        presentValue=0.0,
        units="cubicMeters",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogValueObject(
        objectIdentifier=("analogValue", 110),
        objectName="chA volumetric flow rate, - totalizer",
        presentValue=0.0,
        units="cubicMeters",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 111),
        objectName="chA standard volumetric flow rate",
        presentValue=0.0,
        units="cubicMetersPerHour",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogValueObject(
        objectIdentifier=("analogValue", 112),
        objectName="chA standard volumetric flow rate, + totalizer",
        presentValue=0.0,
        units="cubicMeters",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogValueObject(
        objectIdentifier=("analogValue", 113),
        objectName="chA standard volumetric flow rate, - totalizer",
        presentValue=0.0,
        units="cubicMeters",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 114),
        objectName="chA mass flow",
        presentValue=0.0,
        units="kilogramsPerSecond",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogValueObject(
        objectIdentifier=("analogValue", 115),
        objectName="chA mass flow, + totalizer",
        presentValue=0.0,
        units="kilograms",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogValueObject(
        objectIdentifier=("analogValue", 116),
        objectName="chA mass flow, - totalizer",
        presentValue=0.0,
        units="kilograms",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 117),
        objectName="chA heat flow",
        presentValue=0.0,
        units="watts",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogValueObject(
        objectIdentifier=("analogValue", 118),
        objectName="chA heat flow, + totalizer",
        presentValue=0.0,
        units="megawattHours",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogValueObject(
        objectIdentifier=("analogValue", 119),
        objectName="chA heat flow, - totalizer",
        presentValue=0.0,
        units="megawattHours",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 120),
        objectName="chA concentration",
        presentValue=0.0,
        units="noUnits",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 121),
        objectName="chA SNR",
        presentValue=0.0,
        units="decibels",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 122),
        objectName="chA SCNR",
        presentValue=0.0,
        units="decibels",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 123),
        objectName="chA VariAmp",
        presentValue=0.0,
        units="percent",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 124),
        objectName="chA VariTime",
        presentValue=0.0,
        units="percent",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 125),
        objectName="chA detection rate",
        presentValue=0.0,
        units="percent",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 126),
        objectName="chA diagnostic error bits",
        presentValue=0.0,
        units="noUnits",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 201),
        objectName="chB medium temperature - supply line",
        presentValue=0.0,
        units="degreesCelsius",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 202),
        objectName="chB medium temperature - return line",
        presentValue=0.0,
        units="degreesCelsius",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 203),
        objectName="chB medium pressure - supply line",
        presentValue=0.0,
        units="bars",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 204),
        objectName="chB medium pressure - return line",
        presentValue=0.0,
        units="bars",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 205),
        objectName="chB signal amplitude",
        presentValue=0.0,
        units="noUnits",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 206),
        objectName="chB sound speed",
        presentValue=0.0,
        units="metersPerSecond",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 207),
        objectName="chB flow velocity",
        presentValue=0.0,
        units="metersPerSecond",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 208),
        objectName="chB volumetric flow rate",
        presentValue=0.0,
        units="cubicMetersPerHour",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogValueObject(
        objectIdentifier=("analogValue", 209),
        objectName="chB volumetric flow rate, + totalizer",
        presentValue=0.0,
        units="cubicMeters",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogValueObject(
        objectIdentifier=("analogValue", 210),
        objectName="chB volumetric flow rate, - totalizer",
        presentValue=0.0,
        units="cubicMeters",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 211),
        objectName="chB standard volumetric flow rate",
        presentValue=0.0,
        units="cubicMetersPerHour",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogValueObject(
        objectIdentifier=("analogValue", 212),
        objectName="chB standard volumetric flow rate, + totalizer",
        presentValue=0.0,
        units="cubicMeters",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogValueObject(
        objectIdentifier=("analogValue", 213),
        objectName="chB standard volumetric flow rate, - totalizer",
        presentValue=0.0,
        units="cubicMeters",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 214),
        objectName="chB mass flow",
        presentValue=0.0,
        units="kilogramsPerSecond",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogValueObject(
        objectIdentifier=("analogValue", 215),
        objectName="chB mass flow, + totalizer",
        presentValue=0.0,
        units="kilograms",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogValueObject(
        objectIdentifier=("analogValue", 216),
        objectName="chB mass flow, - totalizer",
        presentValue=0.0,
        units="kilograms",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 217),
        objectName="chB heat flow",
        presentValue=0.0,
        units="watts",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogValueObject(
        objectIdentifier=("analogValue", 218),
        objectName="chB heat flow, + totalizer",
        presentValue=0.0,
        units="megawattHours",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogValueObject(
        objectIdentifier=("analogValue", 219),
        objectName="chB heat flow, - totalizer",
        presentValue=0.0,
        units="megawattHours",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 220),
        objectName="chB concentration",
        presentValue=0.0,
        units="noUnits",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 221),
        objectName="chB SNR",
        presentValue=0.0,
        units="decibels",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 222),
        objectName="chB SCNR",
        presentValue=0.0,
        units="decibels",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 223),
        objectName="chB VariAmp",
        presentValue=0.0,
        units="percent",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 224),
        objectName="chB VariTime",
        presentValue=0.0,
        units="percent",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 225),
        objectName="chB detection rate",
        presentValue=0.0,
        units="percent",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 226),
        objectName="chB diagnostic error bits",
        presentValue=0.0,
        units="noUnits",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 1008),
        objectName="chY volumetric flow rate",
        presentValue=0.0,
        units="cubicMetersPerHour",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogValueObject(
        objectIdentifier=("analogValue", 1009),
        objectName="chY volumetric flow rate, + totalizer",
        presentValue=0.0,
        units="cubicMeters",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogValueObject(
        objectIdentifier=("analogValue", 1010),
        objectName="chY volumetric flow rate, - totalizer",
        presentValue=0.0,
        units="cubicMeters",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 1011),
        objectName="chY standard volumetric flow rate",
        presentValue=0.0,
        units="cubicMetersPerHour",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogValueObject(
        objectIdentifier=("analogValue", 1012),
        objectName="chY standard volumetric flow rate, + totalizer",
        presentValue=0.0,
        units="cubicMeters",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogValueObject(
        objectIdentifier=("analogValue", 1013),
        objectName="chY standard volumetric flow rate, - totalizer",
        presentValue=0.0,
        units="cubicMeters",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 1014),
        objectName="chY mass flow",
        presentValue=0.0,
        units="kilogramsPerSecond",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogValueObject(
        objectIdentifier=("analogValue", 1015),
        objectName="chY mass flow, + totalizer",
        presentValue=0.0,
        units="kilograms",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogValueObject(
        objectIdentifier=("analogValue", 1016),
        objectName="chY mass flow, - totalizer",
        presentValue=0.0,
        units="kilograms",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogInputObject(
        objectIdentifier=("analogInput", 1017),
        objectName="chY heat flow",
        presentValue=0.0,
        units="watts",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogValueObject(
        objectIdentifier=("analogValue", 1018),
        objectName="chY heat flow, + totalizer",
        presentValue=0.0,
        units="megawattHours",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    ),
    AnalogValueObject(
        objectIdentifier=("analogValue", 1019),
        objectName="chY heat flow, - totalizer",
        presentValue=0.0,
        units="megawattHours",
        covIncrement=1.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        reliability="noFaultDetected",
        outOfService=False
    )
]


class SampleApplication(
    BIPSimpleApplication, ReadWritePropertyMultipleServices, ChangeOfValueServices
):
    pass


def main():
    global test_application

    # make a parser
    parser = ConfigArgumentParser(description=__doc__)

    # parse the command line arguments
    args = parser.parse_args()

    # make a device object
    this_device = LocalDeviceObject(ini=args.ini)

    # make a sample application
    test_application = SampleApplication(this_device, args.ini.address)

    # add it to the device
    for eachObject in objectList:
        test_application.add_object(eachObject)

    run()


if __name__ == "__main__":
    main()
