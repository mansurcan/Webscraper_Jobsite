import wget
from selenium import webdriver
import uuid
import os
import time
import Constants
import pandas as pd
from selenium.webdriver.support.select import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By


class Jobsite():
    '''
    This class represents the jobsite.
    It contains the methods to scrape the data from the website.
    '''

    def __init__(self):
        '''
        Initialize the webdriver and the url.
        Chrome options are used to disable the notification pop-up.
        '''
        
        print("Options are initialized...")

        self.NoneType = type(None)

        opt = webdriver.ChromeOptions()
        opt.headless = False
        opt.add_argument("--headless")
        opt.add_argument("--disable-notifications")
        opt.add_argument("--disable-dev-shm-usage")
        opt.add_argument("--disable-gpu")
        opt.add_argument( "--no-sandbox")
        opt.add_argument("--disable-setuid-sandbox",)
        opt.add_argument('--ignore-certificate-errors')
        opt.add_argument("--test-type")
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=opt)
        self.driver.get(Constants.URL)
        self.driver.set_page_load_timeout(10)
        self.driver.implicitly_wait(10)
                
    def _search(self):
        '''
        This method searches for the job on the main page:
        - Select the job title
        - Select the job location
        - Select how far you want to travel
        '''
        
        print("Searching for the job...")

        cookie = self.driver.find_element(by=By.XPATH, value=Constants.COOKIE_XPATH)

        try:
            cookie.click()
        except Exception as e:
            print(e)

        job_title = self.driver.find_element(by=By.ID, value='keywords')
        job_title.click()
        job_title.send_keys('Data Scientist')
        time.sleep(1)

        location = self.driver.find_element(by=By.ID, value='location')
        location.click()
        location.send_keys('London')
        time.sleep(1)

        dropdown = self.driver.find_element(by=By.ID, value='Radius')
        radius = Select(dropdown)
        radius.select_by_visible_text('30 miles')
        time.sleep(2)

        search = self.driver.find_element(by=By.XPATH, value=Constants.SEARCH_XPATH)
        search.click()
        time.sleep(5)

    def create_images_folder(self):
        '''
        Download the images from the job posting.
        '''
        
        print("Create the images folder and download...")  

        img = self.driver.find_elements(by=By.XPATH, value=Constants.IMAGE_XPATH)
        print(len(img))
        
        src = [i.get_attribute('src') for i in img]
        print(len(src))
        
        image_path = os.getcwd()
        image_path = os.path.join(image_path, 'logo_images')
        
        if not os.path.exists(image_path):
            os.mkdir(image_path)
            print(image_path)
            
        count = 0
        
        for s in src:
                    save_as = os.path.join(image_path, 'image_' + str(count) + '.gif')
                    wget.download(s, save_as)     
                    count += 1    
                    # urllib.request.urlretrieve(s, os.path.join(image_path, 'image' + str(count) + '.jpg'))
                    # count += 1
        # count = 0   
        # for s in src:        
        #     try:
        #         if s != None:
        #             # s = str(s)
        #             print(s)
        #             urllib.request.urlretrieve(s, os.path.join(image_path, 'image'+ str(count) + '.jpg'))
        #             count += 1     
        #         else:
        #             raise TypeError
        #     except Exception as e:
        #         print(f'The error is {e}')
            
    def scrape_data(self):
        '''
        It scrapes the data from the job posting.
        - titles, locations, salaries, companies,post dates, descriptions, image links, job references
        and adds uuid to each row.
        '''
        
        print("Scraping the data...")
        
        job_results = []

        for k in range(1):

            titles = self.driver.find_elements(by=By.XPATH, value=Constants.TITLE_XPATH)
            location = self.driver.find_elements(by=By.XPATH, value=Constants.LOCATION_XPATH)
            salary = self.driver.find_elements(by=By.XPATH, value=Constants.SALARY_XPATH)
            company = self.driver.find_elements(by=By.XPATH, value=Constants.COMPANY_XPATH)
            posted = self.driver.find_elements(by=By.XPATH, value=Constants.POSTED_XPATH)
            description = self.driver.find_elements(by=By.XPATH, value=Constants.DESCRIPTION_XPATH)
            job_ref = self.driver.find_elements(by=By.XPATH, value=Constants.JOB_REF_XPATH)
            
            if not self.NoneType in [titles, location, salary, company, posted, description, job_ref]:
                
                for i in range(len(titles)):
                    
                        uuidFour = str(uuid.uuid4()) 
                    
                        data = {'uuid': uuidFour,
                                'job_title': titles[i].text,
                                'location': location[i].text, 
                                'salary': salary[i].text, 
                                'company': company[i].text, 
                                'post_date': posted[i].text, 
                                'description': description[i].text, 
                                'job_reference': job_ref[i].get_attribute('href')}
                        
                        job_results.append(data)
                        
            # next=driver.find_element_by_xpath(Constants.NEXT_XPATH)
            # next.click()
            
                        df_data = pd.DataFrame(job_results, columns=['uuid',
                                                                     'job_title', 
                                                                     'location', 
                                                                     'salary', 
                                                                     'company', 
                                                                     'post_date', 
                                                                     'description', 
                                                                     'job_reference'])
                        
                        df_data.to_excel('Data_Scientist_London.xlsx', index=False)
                        df_data.to_json('Data_Scientist_London.json', orient='records')
                        
            print(df_data)
                            
if __name__ == '__main__':
    '''
    Scrape the job advert data from Jobsite website.
    '''
    
    jobsite = Jobsite()
    jobsite._search()
    jobsite.create_images_folder()
    jobsite.scrape_data()
    
    print("Done!")
    
jobsite.driver.quit()
