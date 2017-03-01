from dblp_xml_processing import XmlProcessing
from pdf_text_extractor import TextExtraction
from classify_and_NEE import classify_and_NEEextraction
import config as cfg
import schedule
import time
import functools
from pyhelpers import tools


# Avoid termination from exceptions
def catch_exceptions(cancel_on_failure=False):
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except:
                import traceback
                print(traceback.format_exc())
                if cancel_on_failure:
                    return schedule.CancelJob
        return wrapper
    return catch_exceptions_decorator


def exist_papers_with_out_content():
  db = tools.connect_to_mongo()
  mongo_string_conf = {'booktitle': {'$in': cfg.booktitles}, 'content': {'$exists': False}}
  mongo_string_journal = {'journal': {'$in': cfg.journals}, 'content': {'$exists': False}}
  count_book = db.publications.find(mongo_string_conf).count()
  count_journal = db.publications.find(mongo_string_journal).count()

  if (count_book + count_journal) > 0:
    # there are pubs with out content
    return True
  else:
    # there are NOT pubs with out content
    return False


@catch_exceptions(cancel_on_failure=False)
def update_process():
  XmlProcessing()
  if exist_papers_with_out_content():
    # if there are papers with out content proceed to text extraction & classify_NEE
    TextExtraction()
    classify_and_NEEextraction()
  else:
    print("No new paper additions!")




def main():
  # create all the necessary folders

  if cfg.updateNow:
    update_process()

  if cfg.checkDaily:
    # perform update every Day
    schedule.every().day.at("18:00").do(update_process)

  if cfg.checkWeekly:
    # Perform update every Friday
    schedule.every().friday.at("18:00").do(update_process)

  # In order to perform  separetly one of the three
  # main phases, all the update features need to be False
  if cfg.updateNow is False and cfg.checkDaily is False and cfg.checkWeekly is False:

    if cfg.only_pdf_download:
      print("Perform XML processing!")
      XmlProcessing()

    if cfg.only_text_extraction:
      print("Perform Text Extraction processing!")
      TextExtraction()

    if cfg.only_classify_nee:
      print("Perform Rhetorical/Name entity extraction and classify!")
      classify_and_NEEextraction()

  while True:
    if not cfg.checkWeekly and not cfg.checkDaily:
      break
    else:
      schedule.run_pending()
      time.sleep(1)

if __name__ == '__main__':
    main()


