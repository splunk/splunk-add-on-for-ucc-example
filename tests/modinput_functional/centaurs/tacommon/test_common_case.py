import copy


class TACommonCase:
    INFO_TAG = "info"

    def __init__(self, input_config=None):
        self.input_config = copy.deepcopy(input_config) if input_config else {}
        self.splunk = None
        self.rest = None
        self.logger = None
        self.test_instance = None

        # check success=1 OR failure=0
        self._check_flag = 1

        self.check_task_list = []

        def check_generator():
            val = None
            for check_task in self.check_task_list:
                while not check_task():
                    if val == self.INFO_TAG:
                        val = (
                            yield f"{check_task.im_class.__name__}.{check_task.__func__.__name__}"
                        )
                    else:
                        val = yield False
            if val == self.INFO_TAG:
                yield f"Failed in conventional process, but finally got success, class: {self.__class__.__name__}"
            else:
                yield True

        self._check_generator = check_generator()

    def check(self):
        return self._check_generator.next()

    def get_check_task_info(self):
        return self._check_generator.send(self.INFO_TAG)

    def bind_splunk(self, splunk):
        self.splunk = splunk

    def bind_rest(self, rest):
        self.rest = rest

    def bind_logger(self, logger):
        self.logger = logger

    def bind_test_instance(self, test_instance):
        self.test_instance = test_instance

    def setup(self):
        self.logger.info(f"In {self.__class__.__name__} setup function")

    def teardown(self):
        self.logger.info(f"In {self.__class__.__name__} teardown function")

    def set_check_flag(self, new_check_flag):
        if new_check_flag in (0, 1):
            self._check_flag = new_check_flag
        else:
            raise ValueError(
                f"check flag only support (0, 1), but got {new_check_flag}"
            )

    def update_input_config(self, **new_config):
        self.input_config.update(new_config)
        return True
