from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel
# from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from python_anticaptcha import AnticaptchaClient, ImageToTextTask
from selenium.webdriver.support.select import Select
from seleniumwire import webdriver
import time 
from typing import Optional, List
import time
from tempfile import mkdtemp
import os
from mangum import Mangum 
import re
import requests

app = FastAPI()


handler = Mangum(app)


data_path = os.path.join("/tmp/data/")
os.makedirs(data_path, exist_ok=True)

class User(BaseModel):
    username : str
    password : str
    PayerId : int
    MemberId : Optional[str]
    InsuranceCompany : Optional[str] = ""
    CorporateName : Optional[str] = ""
    MemberName : Optional[str] = ""
    EmployeeId : Optional[str] = ""
    PolicyNo : Optional[str] = ""
    PolicyType : Optional[str] = ""
    InsuranceCardNo : Optional[str] = ""
    PolicyHolderName : Optional[str] = ""
    MobileNo : Optional[str] = ""
    EmailId : Optional[str] = ""
    RohiniCode : Optional[str] = ""
    ProductCode : Optional[str] = ""
    ProviderId : Optional[str] = ""

class MemberDetails(BaseModel):
    EmployeeCode : Optional[str]
    MemberRelation : Optional[str]
    MemberID : Optional[str]
    PolicyHolderName : Optional[str]
    InsuranceCompanyId : Optional[str]
    InsuranceCompanyName : Optional[str]
    PayerInsuranceId : Optional[str]
    MemberName : Optional[str]
    MemberAge : Optional[int]
    MemberGenderSex : Optional[str]
    PolicyNo : Optional[str]
    MemberEmailId : Optional[str]
    EmployeeName : Optional[str]

class RPASearchMemberResponse(BaseModel):
    IsSuccess : bool 
    ErrorMessage : Optional[str] 
    memberDetails : List[MemberDetails]

def captcha_value(captcha_path):
    api_key = '8b431252eef32b4e4c5c7d9432194fde'
    captcha_fp = open(captcha_path, 'rb')
    client = AnticaptchaClient(api_key)
    task = ImageToTextTask(captcha_fp)
    job = client.createTask(task)
    job.join()
    captcha_value=job.get_captcha_text()
    return captcha_value

class BeneficiarySearch:
    def __init__(self):
#-----------------------------------for lambda------------------------------------------------------------------------------------
        options = webdriver.ChromeOptions()
        options.binary_location = '/opt/chrome/chrome'
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920x1080")
        options.add_argument("--single-process")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-dev-tools")
        options.add_argument("--no-zygote")
        options.add_argument(f"--user-data-dir={mkdtemp()}")
        options.add_argument(f"--data-path={mkdtemp()}")
        options.add_argument(f"--disk-cache-dir={mkdtemp()}")
        options.add_argument("--remote-debugging-port=9222")
        self.driver = webdriver.Chrome("/opt/chromedriver",
                               options=options)
        self.driver.maximize_window()

#-------------------------------------------------for local-----------------------------------------------------------


        # options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        # options.add_argument("--no-sandbox")
        # options.add_argument("--window-size=1920x1080")
        # options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
        # self.driver = webdriver.Chrome(ChromeDriverManager().install() , options = options)

        # self.driver.maximize_window()


#-------------------------------------------------------------------------------------------------------------------------

    def fhpl_beneficiary_search(self, user : User):

        try:
            self.driver.get("https://epreauth.fhpl.net/")
        except:
            raise HTTPException(status_code= 404, detail= "Invalid Portal Link")
        try:
            try:
                user_name = WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[3]/div/div/div/table/tbody/tr[4]/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td[2]/input[1]")))
                user_name.clear()
                user_name.send_keys(user.username)
            except:
                print("Portal Unresponsive")
                return RPASearchMemberResponse(IsSuccess= False, ErrorMessage= 'Portal Inactive or Unresponsive', memberDetails= [])
            
            try: 
                pwd = WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[3]/div/div/div/table/tbody/tr[4]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td[2]/input[1]")))
                pwd.clear()
                pwd.send_keys(user.password)

                login_button = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[3]/div/div/div/table/tbody/tr[4]/td/table/tbody/tr[2]/td/table/tbody/tr[4]/td/input")))
                login_button.click()

                NewPreAuth_button = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[3]/div/div/div/div/table/tbody/tr[1]/td/a[1]")))
                print("Pre Auth Button Found")
            except:
                print("Login Failed, Wrong Credentials")
                return RPASearchMemberResponse(IsSuccess= False, ErrorMessage= 'Login Failed', memberDetails= [])
            time.sleep(3)
            NewPreAuth_button.click()

            try:
                insurance_company_selector = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[3]/div/div/div/div/table/tbody/tr[4]/td/div/div[2]/div[1]/center/table[1]/tbody/tr[2]/td/table/tbody/tr[1]/td[2]/select")))
                print("Insurance Company Field Found")

                insurance_company_selector_drop = Select(insurance_company_selector)
                insurance_company = user.InsuranceCompany

                insurance_company_selector_drop.select_by_visible_text(insurance_company)
                print("Insurance Company Selected")
            except: 
                print("Incorrect Insurance Company")
                return RPASearchMemberResponse(IsSuccess= False, ErrorMessage= 'Incorrect Insurance Company', memberDetails= [])

            if user.MemberId == '':
                corporate_name_element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[3]/div/div/div/div/table/tbody/tr[4]/td/div/div[2]/div[1]/center/table[1]/tbody/tr[2]/td/table/tbody/tr[2]/td[6]/input[1]")))
                corporate_name_element.clear()
                corporate_name_element.send_keys(user.CorporateName)
                print("Corporate Field Found and Entered")

                employee_id_element = WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[3]/div/div/div/div/table/tbody/tr[4]/td/div/div[2]/div[1]/center/table[1]/tbody/tr[2]/td/table/tbody/tr[2]/td[8]/input[1]")))
                employee_id_element.clear()
                employee_id_element.send_keys(user.EmployeeId)
                print("Employee ID found and Entered")

                emp_ID_go_button = WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[3]/div/div/div/div/table/tbody/tr[4]/td/div/div[2]/div[1]/center/table[1]/tbody/tr[2]/td/table/tbody/tr[2]/td[9]/input")))
                emp_ID_go_button.click()
                print("Employee ID Go Button Clicked")

            else:
                uhid_element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[3]/div/div/div/div/table/tbody/tr[4]/td/div/div[2]/div[1]/center/table[1]/tbody/tr[2]/td/table/tbody/tr[2]/td[2]/input")))
                uhid_element.clear()
                uhid_element.send_keys(user.MemberId)
                print("UHID Found and Entered")

                uhid_go_button = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[3]/div/div/div/div/table/tbody/tr[4]/td/div/div[2]/div[1]/center/table[1]/tbody/tr[2]/td/table/tbody/tr[2]/td[3]/input")))
                uhid_go_button.click()
                print("GO BUTTON CLICKED")

            try: 
                patient_field = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[3]/div/div/div/div/table/tbody/tr[4]/td/div/div[2]/div[1]/center/table[3]/tbody[1]/tr[2]/td[2]/input")))
                print("Patient Field Found")
                patient_name_value = patient_field.get_attribute("Value")
                print(patient_name_value)
            except:
                return RPASearchMemberResponse(IsSuccess= False, ErrorMessage='Portal Unresponsive', memberDetails= [])

            if (patient_name_value and str(patient_name_value).strip()) == None:
                print("MemberNot Found")
                return RPASearchMemberResponse(IsSuccess= False, ErrorMessage= 'Member Not Found', memberDetails=[])
            

        except:
            if (patient_name_value and str(patient_name_value).strip()) == None:
                self.driver.find_element(By.XPATH, "/html/body/form/div[3]/div/div/nav/ul/li[2]/input").click()
                print("MemberNot Found")
                return RPASearchMemberResponse(IsSuccess= False, ErrorMessage= 'Member Not Found', memberDetails=[])
        else:
            uhid_element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[3]/div/div/div/div/table/tbody/tr[4]/td/div/div[2]/div[1]/center/table[1]/tbody/tr[2]/td/table/tbody/tr[2]/td[2]/input")))
            uhid_element_value = uhid_element.get_attribute("Value")
            print(uhid_element_value)

            corporate_name_element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[3]/div/div/div/div/table/tbody/tr[4]/td/div/div[2]/div[1]/center/table[1]/tbody/tr[2]/td/table/tbody/tr[2]/td[6]/input[1]")))
            corporate_name_value = corporate_name_element.get_attribute("Value")
            print(corporate_name_value)

            employee_id_element = WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[3]/div/div/div/div/table/tbody/tr[4]/td/div/div[2]/div[1]/center/table[1]/tbody/tr[2]/td/table/tbody/tr[2]/td[8]/input[1]")))
            employee_id_value = employee_id_element.get_attribute("Value")
            print(employee_id_value)

            gender_field = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[3]/div/div/div/div/table/tbody/tr[4]/td/div/div[2]/div[1]/center/table[3]/tbody[1]/tr[2]/td[4]/select")))
            gender_field_select = Select(gender_field)
            gender_field_select = gender_field_select.first_selected_option 
            gender_field_selected_value = gender_field_select.text
            print(gender_field_selected_value)

            relationship_field = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[3]/div/div/div/div/table/tbody/tr[4]/td/div/div[2]/div[1]/center/table[3]/tbody[1]/tr[3]/td[2]/select")))
            relationship_field_select = Select(relationship_field)
            relationship_field_select = relationship_field_select.first_selected_option
            relationship_field_select_value = relationship_field_select.text
            print(relationship_field_select_value)

            dob_field = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[3]/div/div/div/div/table/tbody/tr[4]/td/div/div[2]/div[1]/center/table[3]/tbody[1]/tr[3]/td[4]/input")))
            dob_field_value = dob_field.get_attribute("Value")
            print(dob_field_value)

            age_field = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[3]/div/div/div/div/table/tbody/tr[4]/td/div/div[2]/div[1]/center/table[3]/tbody[1]/tr[4]/td[2]/input")))
            age_field_value = age_field.get_attribute("Value")
            print(age_field_value)

            patient_mobile_number_field = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[3]/div/div/div/div/table/tbody/tr[4]/td/div/div[2]/div[1]/center/table[3]/tbody[1]/tr[4]/td[4]/input")))
            patient_mobile_number_value = patient_mobile_number_field.get_attribute("Value")
            print(patient_mobile_number_value)

            policy_no_field = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[3]/div/div/div/div/table/tbody/tr[4]/td/div/div[2]/div[1]/center/table[3]/tbody[2]/tr[1]/td[4]/input")))
            policy_no_value = policy_no_field.get_attribute("Value")
            print(policy_no_value)

            self.driver.find_element(By.XPATH, "/html/body/form/div[3]/div/div/nav/ul/li[2]/input").click()

            member_details_list = []
            
            member_details = MemberDetails(MemberName= patient_name_value , MemberGenderSex=gender_field_selected_value, MemberRelation=relationship_field_select_value, MemberAge=age_field_value, PolicyNo=policy_no_value, EmployeeCode= employee_id_value,InsuranceCompanyName= insurance_company,PolicyHolderName= corporate_name_value , MemberID= uhid_element_value)
            member_details_list.append(member_details)
            print(member_details_list)
            
            return RPASearchMemberResponse(IsSuccess= True, ErrorMessage= None, memberDetails= member_details_list)

        finally:
            self.driver.quit()


    #PARAMOUNT BENEFICIARY SEARCH FLOW

    def paramount_beneficiary_search(self, user: User):
            self.driver.get("https://provider.paramounttpa.com/Login.aspx")
            
            username_field = WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[3]/div[2]/div[1]/div/div/div/div[2]/fieldset/input[1]")))
            username_field.clear()
            username_field.send_keys(user.username)
            print("UserName Field Found")
                
            retry = 0

            while(retry<=5):
                
                password_field = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[3]/div[2]/div[1]/div/div/div/div[2]/fieldset/input[2]")))
                password_field.clear()
                password_field.send_keys(user.password)
                print("Password Field Found")

                captcha_path = '/tmp/data/foo.png'
                self.driver.find_element(By.XPATH, "/html/body/form/div[3]/div[2]/div[1]/div/div/div/div[2]/fieldset/div/div[1]/div/b/span").screenshot(captcha_path)
                print("Captcha screenshot")

                captcha_enter_field = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[3]/div[2]/div[1]/div/div/div/div[2]/fieldset/div/div[2]/input")))
                print("Captcha Field Found")

                enter_captcha_value = captcha_value(captcha_path)
                print(enter_captcha_value)
                captcha_enter_field.clear()
                captcha_enter_field.send_keys(enter_captcha_value)
                print("Captcha Value Entered")

                login_button = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[3]/div[2]/div[1]/div/div/div/div[2]/fieldset/input[3]")))
                print("Login Button Found - 1")
                login_button.click()
                print("Login Button Found")

                try:
                    alert = WebDriverWait(self.driver, 3).until(EC.alert_is_present())
                    print(alert.text)
                    try:
                        if 'Invalid Captcha Code' in alert.text:
                            alert.accept()
                            retry += 1
                            print(retry, 'retry count.....')
                            continue
                        elif 'Something went wrong,Kindly contact with Administration' in alert.text:
                            alert.accept()
                            self.driver.quit()
                            print("Invalid Credentials")
                            return RPASearchMemberResponse(IsSuccess= False, ErrorMessage= 'Invalid Credentials', memberDetails= [])
                        
                    except:
                        print("Invalid Captcha")
                        return RPASearchMemberResponse(IsSuccess=False, ErrorMessage= "Invalid Captcha", memberDetails= [])
                    
                except:
                    break
                
            time.sleep(2)

            # e_cashless_element = WebDriverWait(self.driver,5).until(EC.presence_of_element_located((By.XPATH, "/html/body/form/section/div/section/header/div[2]/li[2]/a")))
            # print({"Login": True})
            # e_cashless_element.click()

            # try:
            #     fresh_request_element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/section/div/section/header/div[2]/li[2]/ul/li[1]/a")))
            #     fresh_request_element.click()
#working on lambda --------------------------------------------------            
            
            retry=0
            while retry<=10:
                try:
                    e_cashless_element = WebDriverWait(self.driver,5).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/section/div/section/header/div[2]/li[2]/a")))
                    e_cashless_element.click()
                    retry = 11
                except:
                    print("Retrying E-Cashless element",retry)
                    retry +=1
                    time.sleep(1)
                    continue

            fresh_request_element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/section/div/section/header/div[2]/li[2]/ul/li[1]/a")))
            fresh_request_element.click()
            time.sleep(2)

            individual_policy_type = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/section/div/section/div/section/section/div/section/div/div/div[4]/div[1]/div[2]/table/tbody/tr/td[1]/input")))
            corporate_policy_type = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/section/div/section/div/section/section/div/section/div/div/div[4]/div[1]/div[2]/table/tbody/tr/td[2]/input")))

            try:
                if user.MemberId == '':

                    if(user.PolicyType == 'Individual' and individual_policy_type.is_selected()):

                        time.sleep(1)

                        try:
                            insurance_company_selector = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/section/div/section/div/section/section/div/section/div/div/div[4]/div[2]/div[2]/select")))
                            print("Insurance Company Field Found")

                            insurance_company_selector_dropdown = Select(insurance_company_selector)
                            insurance_company = user.InsuranceCompany

                            insurance_company_selector_dropdown.select_by_visible_text(insurance_company)
                            print("Insurance Company Selected")
                        except:
                            print("Incorrect Insurance Company")
                            return RPASearchMemberResponse(IsSuccess= False, ErrorMessage='Incorrect Insurance Company', memberDetails=[])

                        insurance_card_no_element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/section/div/section/div/section/section/div/section/div/div/div[4]/div[2]/div[4]/input")))
                        insurance_card_no_element.clear()
                        insurance_card_no_element.send_keys(user.InsuranceCardNo)
                        print("Insurance Card No entered")

                        policy_no_element  = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/section/div/section/div/section/section/div/section/div/div/div[4]/div[2]/div[6]/input")))
                        policy_no_element.clear()
                        policy_no_element.send_keys(user.PolicyNo)

                        individual_policy_search_button = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/section/div/section/div/section/section/div/section/div/div/div[4]/div[2]/div[7]/input")))
                        individual_policy_search_button.click()

                    elif(user.PolicyType == 'Corporate' or corporate_policy_type.is_selected()):

                        corporate_policy_type.click()
                        time.sleep(2)

                        corporate_name_selector = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/section/div/section/div/section/section/div/section/div/div/div[4]/div[2]/div[2]/div/a")))
                        corporate_name_selector.click()

                        corporate_name_selector_search_field = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[5]/div/input")))
                        corporate_name_selector_search_field.send_keys(user.CorporateName)
                        corporate_name_selector_search_field.send_keys(Keys.ENTER)
                        time.sleep(2)

                        employee_no_element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/section/div/section/div/section/section/div/section/div/div/div[4]/div[2]/div[4]/input")))
                        employee_no_element.clear()
                        employee_no_element.send_keys(user.EmployeeId)

                        corporate_search_button = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/section/div/section/div/section/section/div/section/div/div/div[4]/div[2]/div[5]/input")))
                        corporate_search_button.click()
                        time.sleep(1)

                    else:
                        print("Wrong PolicyType Entered")
                        return RPASearchMemberResponse(IsSuccess= False, ErrorMessage='Wrong PolicType Entered', memberDetails=[])

                else:

                    phs_id_element = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/section/div/section/div/section/section/div/section/div/div/div[1]/div[2]/input")))
                    phs_id_element.clear()
                    phs_id_element.send_keys(user.MemberId)


                    phs_id_search_element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/section/div/section/div/section/section/div/section/div/div/div[1]/div[3]/input")))
                    phs_id_search_element.click()

                    time.sleep(2)

                policy_info_element = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located((By.XPATH, "/html/body/form/section/div/section/div/section/section/div[2]/section/div")))

            except:
                print("Member Not Found")
                return RPASearchMemberResponse(IsSuccess= False, ErrorMessage= 'Member Not Found', memberDetails= [])
            else:
                tbody = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/form/section/div/section/div/section/section/div[2]/section/div/div/table")))

                trs = tbody.find_elements(By.TAG_NAME, "tr")
                member_detail_list = []

                for tr in trs:
                    tds = tr.find_elements(By.TAG_NAME, "td")
                  
                    parts = tds[0].get_attribute("innerText")
                    if len(parts) > 8:
                        relation = re.search(r"Relation\s*:\s*(\w+)", parts).group(1)
                        beneficiary_name = re.search(r"Beneficiary Name\s*:\s*([\w\s]+)", parts).group(1)
                        policy_no = re.search(r"Policy No\s*:\s*(\w+)", parts).group(1)

                        print(f"Relation: {relation}")
                        print(f"Beneficiary Name: {beneficiary_name}")
                        print(f"Policy No: {policy_no}")

                        result = {
                            
                            "Name": beneficiary_name.replace("Policy No", "").strip() ,
                            "Relationship": relation,
                            "PolicyNo": policy_no
                        }

                        member_details = MemberDetails(MemberName= result["Name"], MemberRelation= result["Relationship"], PolicyNo= result["PolicyNo"])
                        member_detail_list.append(member_details)

                print(member_detail_list)
                return RPASearchMemberResponse(IsSuccess= True, ErrorMessage= None, memberDetails= member_detail_list)
            finally:
                self.driver.quit()


    def star_beneficiary_search(self, user: User): 

        self.driver.get("https://shpv.starhealth.in/")
        user_name_field = WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-home/div/div[2]/app-login/div/form/p[2]/span/input")))        
        user_name_field.clear()
        user_name_field.send_keys(user.username)
        print("UserName Element Found")

        pwd_field = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-home/div/div[2]/app-login/div/form/p[3]/span/input")))
        pwd_field.clear()
        pwd_field.send_keys(user.password)
        print("PassWord Element Found")

        login_button = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-home/div/div[2]/app-login/div/form/button")))
        login_button.click()
        print("Login Button Clicked")

        time.sleep(2)

        

        try:
            pre_auth_button = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-pre-auth/div[2]/div/app-claims/div[1]/div[1]/button")))
            print("PreAuth Button Found")
        except Exception as e:
            print(str(e))
            self.driver.quit() 
            return RPASearchMemberResponse(IsSuccess=False, ErrorMessage='Invalid Credentials', memberDetails= [])
        
        headers = self.driver.requests
        for req in headers:
            x_auth_token = req.headers.get("x-auth-token")
            if x_auth_token:
                break

        if x_auth_token:
            print(f"Found x-auth-token: {x_auth_token}")
        else:
            print("x-auth-token not found in headers")
            self.driver.quit() 
            return RPASearchMemberResponse(IsSuccess= False, ErrorMessage= 'X-Auth-Token Not Found', memberDetails= [])
        
        try: 
            pre_auth_button.click()
            print("PreAuth Button Clicked")
            time.sleep(1)

            # claim_type = user.ClaimType
            policy_type = user.PolicyType
            print(policy_type)

            # covid_regex = re.compile(r"(?i)^COVID$")
            # non_covid_regex = re.compile(r"(?i)^NON-COVID$")
            individual_regex = re.compile(r"(?i)^(Individual|Floater)$")
            corporate_regex = re.compile(r"(?i)^(Corporate|Group)$")

            # if covid_regex.match(claim_type):
            #     claim_type_covid_radio = self.driver.find_element(By.XPATH, "/html/body/app-root/app-pre-auth/div[2]/div/app-create-claim/div/app-patient-details/div[7]/div/form/div[2]/p/span[1]/input")
            #     claim_type_covid_radio.click()
            # elif non_covid_regex.match(claim_type):
            #     claim_type_non_covid_radio = self.driver.find_element(By.XPATH, "/html/body/app-root/app-pre-auth/div[2]/div/app-create-claim/div/app-patient-details/div[7]/div/form/div[2]/p/span[2]/input")
            #     claim_type_non_covid_radio.click()
            # else:
            #     self.driver.quit() 
            #     return RPASearchMemberResponse(IsSuccess=False, ErrorMessage= 'Unknown ClaimType Value', memberDetails= [])
            
            if individual_regex.match(policy_type):
                individual_radio = self.driver.find_element(By.XPATH, "/html/body/app-root/app-pre-auth/div[2]/div/app-create-claim/div/app-patient-details/div[7]/div/form/div[4]/p/span[1]/input")
                individual_radio.click()
                print("Individual PolicyType Selected")
                time.sleep(1)
            elif corporate_regex.match(policy_type):
                corporate_radio = self.driver.find_element(By.XPATH, "/html/body/app-root/app-pre-auth/div[2]/div/app-create-claim/div/app-patient-details/div[7]/div/form/div[4]/p/span[2]/input")
                corporate_radio.click()
                print("Corporate PolicyType Selected")
                time.sleep(1)
            else:
                self.driver.quit()
                print("Unknown PolicyType")
                return RPASearchMemberResponse(IsSuccess=False, ErrorMessage= 'Unknown PolicyType', memberDetails= [])
            
            patient_name_element = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-pre-auth/div[2]/div/app-create-claim/div/app-patient-details/div[1]/div[2]/div/div/section/div[1]/form/div[1]/p[1]/span/input")))
            patient_name_element.clear()
            patient_name_element.send_keys(user.MemberName)
            print("Patient name found, MemberName sent")

            if individual_regex.match(policy_type):

                if user.MemberId == "":
                    click_policy_element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-pre-auth/div[2]/div/app-create-claim/div/app-patient-details/div[1]/div[2]/div/div/section/div[1]/form/div[1]/p[2]/label/i")))
                    click_policy_element.click()

                    time.sleep(1)

                    policy_no_element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-pre-auth/div[2]/div/app-create-claim/div/app-patient-details/div[1]/div[2]/div/div/section/div[1]/form/div[1]/p[2]/span/input")))
                    policy_no_element.clear()
                    policy_no_element.send_keys(user.PolicyNo)

                else:
                    member_id_element = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-pre-auth/div[2]/div/app-create-claim/div/app-patient-details/div[1]/div[2]/div/div/section/div[1]/form/div[1]/p[2]/span/input")))
                    member_id_element.clear()
                    member_id_element.send_keys(user.MemberId)

            elif corporate_regex.match(policy_type):

                if user.MemberId == "":
                    click_policy_element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-pre-auth/div[2]/div/app-create-claim/div/app-patient-details/div[1]/div[2]/div/div/section/div[1]/form/div[1]/p[2]/label/i")))
                    click_policy_element.click()

                    time.sleep(1)

                    policy_no_element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-pre-auth/div[2]/div/app-create-claim/div/app-patient-details/div[1]/div[2]/div/div/section/div[1]/form/div[1]/p[2]/span/input")))
                    policy_no_element.clear()
                    policy_no_element.send_keys(user.PolicyNo)

                else:
                    member_id_element = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-pre-auth/div[2]/div/app-create-claim/div/app-patient-details/div[1]/div[2]/div/div/section/div[1]/form/div[1]/p[2]/span/input")))
                    member_id_element.clear()
                    member_id_element.send_keys(user.MemberId)

                if user.EmployeeId == "":
                    click_company_name_element = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-pre-auth/div[2]/div/app-create-claim/div/app-patient-details/div[1]/div[2]/div/div/section/div[1]/form/div[1]/div/p/label/i")))
                    click_company_name_element.click()

                    time.sleep(1)

                    company_name_element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-pre-auth/div[2]/div/app-create-claim/div/app-patient-details/div[1]/div[2]/div/div/section/div[1]/form/div[1]/div/p/span/input")))
                    company_name_element.clear()
                    company_name_element.send_keys(user.CorporateName)

                else: 
                    employee_id_element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-pre-auth/div[2]/div/app-create-claim/div/app-patient-details/div[1]/div[2]/div/div/section/div[1]/form/div[1]/div/p/span/input")))
                    employee_id_element.clear()
                    employee_id_element.send_keys(user.EmployeeId)

            else:
                print("Wrong PolicyType")
                return RPASearchMemberResponse(IsSuccess= False, ErrorMessage= 'Wrong PolicyType', memberDetails= [])

            

            proceed_button = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-pre-auth/div[2]/div/app-create-claim/div/app-patient-details/div[1]/div[2]/div/div/section/div[1]/form/div[2]/p/span/input")))
            proceed_button.click()

            try: 
                alert = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located((By.XPATH, "/html/body/app-root/app-pre-auth/app-alert/div/div[2]/div/div/section")))
                print("MemberDetails Not Found")
                return RPASearchMemberResponse(IsSuccess= False, ErrorMessage='MemberDetails Not Found', memberDetails= [])
            except: 
                pass 

        except:
            pass 
        
        else: 
            member_search_api_url = f'https://a2s.starhealth.in/rules-engine/api/v2/claim/subscriber/details?medicalCardNumber={user.MemberId}&policyNumber=&patientName={user.MemberName}'

            headers = {
                'X-Auth-Token':  x_auth_token,
            }
            time.sleep(2)

            response = requests.get(member_search_api_url, headers= headers)
            print(response)

            if response.status_code == 200: 
                time.sleep(2)
                response_data = response.json()

            print(response_data)

            member_details_list = []
            member_details = MemberDetails(MemberID= response_data['data'][0]['medicalCardNumber'], 
                                            MemberName= response_data['data'][0]['insuredName'], 
                                            PolicyNo= response_data['data'][0]['policyNumber'],
                                            MemberGenderSex=response_data['data'][0]['gender'])
            member_details_list.append(member_details)

            print(member_details_list)     
            return RPASearchMemberResponse(IsSuccess= True, ErrorMessage= None, memberDetails= member_details_list)
        
        finally: 
            self.driver.quit()

    def icici_beneficiary_search(self, user: User):
        try:
            self.driver.get(user.portal_link)
            self.driver.maximize_window()
            username_field = WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[3]/div[2]/div/div[2]/form/p[1]/input")))
        except:
            raise HTTPException(status_code=404)

        retry = 0

        while(retry <= 3): 

            print("UserName_Field Successfully Retrieved")
            username_field.clear()
            username_field.send_keys(user.username)
            print("UserName Successfully Entered")

            password_field = WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[3]/div[2]/div/div[2]/form/p[2]/input")))
            print("PasswordField Successfully Retreived")
            password_field.clear()
            password_field.send_keys(user.password)
            print("Password Successfully Entered")

            captcha_path=r'/tmp/data/foo.png'
            self.driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div[2]/div/div[2]/form/h5").screenshot(captcha_path)
            print("Captcha Screenshot Done ")

            captcha_enter_field = WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[3]/div[2]/div/div[2]/form/p[3]/input")))
            enter_captcha_value = captcha_value(captcha_path)
            print(enter_captcha_value)
            captcha_enter_field.clear()
            captcha_enter_field.send_keys(enter_captcha_value)
            print("Captcha Successfully Entered")

            login_button = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[3]/div[2]/div/div[2]/form/div[2]/input")))
            login_button.click()
            print("Login Button Found")

            try:
                alert = WebDriverWait(self.driver, 3).until(EC.alert_is_present())
                print(alert.text)
                try:
                    if 'Please enter correct Captcha' in alert.text:
                        alert.accept()
                        retry += 1
                        continue
                    elif 'Invalid User Name or Password.' in alert.text:
                        alert.accept()
                        self.driver.quit()
                        return RPASearchMemberResponse(isSuccess= False, message= "Invalid Credentials")
                except:
                    self.driver.quit()
                    return RPASearchMemberResponse(isSuccess= False, message= "Invalid Captcha")
            
            except:
                break

            LoginAlert = WebDriverWait(self.driver, 3).until(EC.alert_is_present())
            print(LoginAlert)
            LoginAlert.accept()

            cashless_request_element = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[3]/div[1]/div/ul/li[1]/div[1]/div[1]/span[1]/a")))
            cashless_request_element.click()

            search_button = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[3]/div/div[4]/form/p/input[1]")))

            try:
                if user.MemberId == '':
                    policy_number_element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[3]/div/div[4]/form/p/input[1]")))
                    policy_number_element.clear()
                    policy_number_element.send_keys(user.PolicyNo)

                    emp_id_element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[3]/div/div[4]/form/div/table/tbody/tr[1]/td[4]/input")))
                    emp_id_element.clear()
                    emp_id_element.send_keys(user.EmployeeId)

                    policy_name_element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[3]/div/div[4]/form/div/table/tbody/tr[2]/td[2]/input")))
                    policy_name_element.clear()
                    policy_number_element.send_keys(user.PolicyHolderName)

                    employee_name_element = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[3]/div/div[4]/form/div/table/tbody/tr[2]/td[4]/input")))
                    employee_name_element.clear()
                    employee_name_element.send_keys(user.MemberName)

                    search_button.click()

                else:
                    UHID_element = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[3]/div/div[4]/form/input[10]")))
                    UHID_element.clear()
                    UHID_element.send_keys(user.MemberId)

                    search_button.click()

                table_element = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div/div[3]/div/div[5]")))

            except: 
                print("No MemberDetails Found")
                return RPASearchMemberResponse(IsSuccess= False, ErrorMessage='MemberDetails Not Found', memberDetails= [])
            
            else:
                pass 

            finally:
                self.driver.quit()






        


@app.post("/BeneficiarySearch")
def payer(user : User):
    if user.PayerId == 523429:
        return  BeneficiarySearch().fhpl_beneficiary_search(user)
    elif user.PayerId == 522940:
        return BeneficiarySearch().paramount_beneficiary_search(user)
    elif user.PayerId == 523408:
        return BeneficiarySearch().star_beneficiary_search(user)
    elif user.PayerId == 522927:
        return BeneficiarySearch().icici_beneficiary_search(user)
    else:
        return RPASearchMemberResponse(IsSuccess= False, ErrorMessage= 'Invalid PayerID', memberDetails= [])

    



