from dblp_xml_processing import XmlProcessing
from pdf_text_extractor import TextExtraction
from classify_and_NEE import classify_and_NEEextraction
from pyhelpers import tools
import config as cfg
import schedule
import time

def update_process():
  XmlProcessing()
  TextExtraction()
  classify_and_NEEextraction()



def main():
  # create all the necessary folders
  tools.create_all_folders()
  if cfg.updateNow:
    update_process()

  if cfg.checkDaily:
    # perform update every Day
    schedule.every().day.at("18:00").do(update_process)

  if cfg.checkWeekly:
    # Perform update every Friday
    schedule.every().friday.at("18:00").do(update_process)

  while True:
    if not cfg.checkWeekly and not cfg.checkDaily:
      break
    else:
      schedule.run_pending()
      time.sleep(1)

if __name__ == '__main__':
    main()


