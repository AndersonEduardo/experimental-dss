from updatechecker import *
from dispatcher import *

def launch(event, context):

    print('[STATUS] - Instiating UpdateChecker...')
    update_checker = UpdateChecker()
    print('[STATUS] - ...done.')

    print('[STATUS] - Instiating Dispatcher...')
    dispatcher = Dispatcher()
    print('[STATUS] - ...done.')

    print('[STATUS] - Checking for updates...')
    updates = update_checker.check_for_updates()
    print('[STATUS] - ...done.')

    print('[STATUS] - Sending email...')
    dispatcher.send_email(updates)
    print('[STATUS] - ...done.')


if __name__ == '__main__':

    launch(None, None)
