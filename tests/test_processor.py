from duplicate_url_discarder import Processor


def test_processor_empty():
    processor = Processor([])
    assert processor.process_url("http://foo.example") == "http://foo.example"
