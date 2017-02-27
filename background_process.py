from dblp_xml_processing import XmlProcessing
from pdf_text_extractor import TextExtraction
from pyhelpers import tools
import config as cfg
import schedule
import time

def update_process():
  try:
    XmlProcessing()
    TextExtraction()
    return True
  except BaseException:
    return False


def main():
  # create all the necessary folders
  tools.create_all_folders()
  if cfg.updateNow:
    update_process()

  if cfg.checkDaily:
    # perform update every Monday
    schedule.every().day.at("10:30").do(update_process)

  if cfg.checkWeekly:
    schedule.every().friday.at("18:00").do(update_process)

  while True:
    schedule.run_pending()
    time.sleep(1)

if __name__ == '__main__':
    main()


