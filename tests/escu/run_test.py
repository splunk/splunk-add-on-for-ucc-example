import json
import sys

import attack_range
from junitparser import Attr, Error, IntAttr, JUnitXml, TestCase, TestSuite

results = attack_range.main(sys.argv[1:])

TestCase.result_count = IntAttr("result_count")
TestCase.detection_file = Attr("detection_file")
TestCase.splunk_search = Attr("splunk_search")

test_suite = TestSuite("escu")

for test_case in results:
    detection_result = test_case.get("detection_result")
    if detection_result.get("runDuration"):
        tc = TestCase(
            name=detection_result.get("detection_name"),
            classname="test.escu",
            time=float(detection_result.get("runDuration")),
        )
        tc.result_count = int(detection_result.get("resultCount"))
        tc.detection_file = detection_result.get("detection_file")
        tc.splunk_search = detection_result.get("splunk_search")
        if detection_result.get("error"):
            er = Error(detection_result.get("messages"))
            if test_case.get("baselines_result"):
                er.text = json.dumps(test_case.get("baselines_result"))
            tc.result = [er]
        test_suite.add_testcase(tc)
    else:
        tc = TestCase(
            name=detection_result.get("detection_name"),
            classname="test.escu",
            time=0,
        )
        tc.detection_file = detection_result.get("detection_file")
        er = Error("Unable to run detection")
        er.text = json.dumps("Check attack_range.log file for more details")
        tc.result = [er]
        test_suite.add_testcase(tc)
xml = JUnitXml()
xml.add_testsuite(test_suite)
xml.write("test-result.xml")

