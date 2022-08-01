import json, argparse, logging
from robonomicsinterface import Account, Datalog
import telegram_notifier
from pinatapy import PinataPy
from datetime import datetime


def pin_folder_to_pinata(config, path, ipfs_destination_path):
    pinata = PinataPy(config["PINATA_API"], config["PINATA_SECRET"])
    return pinata.pin_file_to_ipfs(path, ipfs_destination_path=ipfs_destination_path, save_absolute_paths=False)


def send_datalog(config, datalog_message):
    account = Account(remote_ws=config['ROBONOMICS_ENDPOINT'], seed=config['MNEMONIC'])
    datalog_rws = Datalog(account, rws_sub_owner=config["SUBSCRIPTION_OWNER"])
    res = datalog_rws.record(datalog_message)
    return (datalog_message, res)


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--datapath', '-d', required=True, help='Path to the data folder')
    args = parser.parse_args()

    # Read main config 
    config_file = open("config.json")
    config = json.load(config_file)
    config_file.close()

    pin = pin_folder_to_pinata(config, args.datapath, config["PINATA_IPFS_DESTINATION_PATH"])
    
    datalog_message = pin["IpfsHash"]
    
    try:
        data_str, res = send_datalog(config, datalog_message)
        print(data_str, res)
        msg = "[DONE]: \n Data: %s\nExtrinsic hash: %s" % (data_str, res)
    except Exception as e:
        msg = "[ERROR]: \n %s" % (e)
        
    telegram_notifier.basic_notifier(
        logger_name='training_notifier',
        token_id=config["TELEGRAM_TOKEN_ID"],
        chat_id=config["TELEGRAM_CHAT_ID"],
        message=msg,
        level=logging.INFO
    )