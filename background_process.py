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
  XmlProcessing(booktitles=None, journals=None)
  if exist_papers_with_out_content():
    # if there are papers with out content proceed to text extraction & classify_NEE
    TextExtraction(booktitles=None, journals=None)
    classify_and_NEEextraction(booktitles=None, journals=None)
  else:
    print("No new paper additions!")




def main():
  # create all the necessary folders
  import argparse
  parser = argparse.ArgumentParser()

  # optional parameters to increase the modularity of the script
  # you can start multiple parallel scripts with different conferences or journals
  parser.add_argument("--conf", help="Provide the (Only one) conference you like")
  parser.add_argument("--journal", help="Provide the (Only one) journal you like")
  args, leftovers = parser.parse_known_args()

  booktitles = None
  journals = None

  if args.conf is None and args.journal is None:
    print("No optional parameter proceed with configuration file")
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
        XmlProcessing(booktitles=None, journals=None)

      if cfg.only_text_extraction:
        print("Perform Text Extraction processing!")
        TextExtraction(booktitles=None, journals=None)

      if cfg.only_classify_nee:
        print("Perform Rhetorical/Name entity extraction and classify!")
        classify_and_NEEextraction(booktitles=None, journals=None)

    while True:
      if not cfg.checkWeekly and not cfg.checkDaily:
        break
      else:
        schedule.run_pending()
        time.sleep(1)

  elif args.conf is not None or args.journal is not None:
    if args.conf is not None:
      booktitles = [str(args.conf)]
    if args.journal is not None:
      journals = [str(args.journal)]

    if cfg.only_pdf_download:
      print("Perform XML processing!")
      XmlProcessing(booktitles=booktitles, journals=journals)

    if cfg.only_text_extraction:
      print("Perform Text Extraction processing!")
      TextExtraction(booktitles=booktitles, journals=journals)

    if cfg.only_classify_nee:
      print("Perform Rhetorical/Name entity extraction and classify!")
      classify_and_NEEextraction(booktitles=booktitles, journals=journals)




if __name__ == '__main__':
    main()


