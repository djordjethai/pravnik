import os

from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
from locale import LC_TIME, setlocale
from pravnik_fukncije import dl_parlament, lista_zakona, sumiraj_zakone
from re import search
from requests import get

from myfunc.mojafunkcija import send_email
from myfunc.prompts import PromptDatabase

# Set the locale to Serbian
setlocale(LC_TIME, 'sr_RS.utf8')
# setlocale(LC_TIME, 'sr_RS.utf8@latin')  # za nas linux !!!

# prikuplja podatke o zakonima sa sajtova i salje mail obavestenja sa linkovima na izmene i dopune zakona
#	https://www.paragraf.rs/izmene_i_dopune/
#	http://www.parlament.gov.rs/akti/doneti-zakoni/doneti-zakoni.1033.html  

# skida zakone sa sajta parlament.gov.rs                                                                                                                         
def procitaj_parlament():
    
    # URL of the webpage you want to scrape
    url = 'http://www.parlament.gov.rs/akti/doneti-zakoni/doneti-zakoni.1033.html' 
    suma = ""
    # Send a GET request to the webpage
    response = get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the webpage
        encoding = response.encoding if 'charset' in response.headers.get('content-type', '').lower() else None
        soup = BeautifulSoup(response.content, 'html.parser', from_encoding=encoding)
        
        # Find all the <li> elements with class "td"
        tr_elements = soup.find_all('tr')
        # Iterate through the <li> elements and extract the href attribute from the <a> tags within them
        izvestaj = ""
        
        for tr in tr_elements:
            link = tr.find('a')
            datum = ""
            date_str = "01. Januar 2020."
            date_obj = date.today()
            if link:
                    # Find the <td nowrap> element within the current <tr>
                    td_nowrap = tr.find('td', {"nowrap": True})
        
                    if td_nowrap:
                        # Extract and print the text from the <td nowrap> element
                        datum = td_nowrap.get_text()

            pattern = r'\d{1,2}\.\s\w+\s\d{4}'
            match = search(pattern, datum)

            if match:
                date_str = match.group(0)  # Get the matched date string
                try: 
                    date_obj = datetime.strptime(date_str, "%d. %B %Y").date()  # Convert it to a date object
                except ValueError:
                    pass
            
            target_date = date.today() - timedelta(days=2)
            
            if link and date_obj > target_date:

            # if link and "decembar 2023" in datum:
                href = link.get('href')
                description = link.get_text()
                print("Proveravam: ", description)
                if href and description:
                    mojalista_zakona = lista_zakona()
                    # samo relevantni zakoni
                    
                    for zakon in mojalista_zakona:
                        if zakon.lower() in description.lower():
                            link = "http://www.parlament.gov.rs" + href.replace(" ", "%20")
                            print(" ")
                            print("------------------------------------------------------------------------------------------------")
                            print("Obradjujem: ", description)
                            print("------------------------------------------------------------------------------------------------")
                            print(" ")
                            # Perform your desired action with the matching link
                            ime_fajla = dl_parlament(link)
                            suma = sumiraj_zakone(ime_fajla, description)
                            izvestaj += f"Sa sajta {url} sumiram zakon sa linka {link} \n\n Evo i krakog pregleda zakona: \n\n {suma} \n\n"

        return izvestaj


# prima ceo tekst maila, sa sve linkovima i sa sezecima
def main():
    print(" ")
    print("------------------------------------------------------------------------------------------------")
    print(" ")
    print("AI Pravnik - Ver 20.11.23 - local - pass Env")
    print(" ")
    print("------------------------------------------------------------------------------------------------")
    print(" ")
    text_maila = procitaj_parlament()
    if len(text_maila ) > 3:
        with PromptDatabase() as db:
            prompt_map = db.get_prompts_by_names(['new_law_email'], [os.getenv("NEW_LAW_EMAIL")])
        uputstvo = prompt_map.get("new_law_email", "You are helpful assistant").format(text_maila=text_maila)      
               
        print(" ")
        print("------------------------------------------------------------------------------------------------")
        print(" ")
        print("ZAVRSENA OBRADA, SALJEM MAIL")
        print(" ")
        print("------------------------------------------------------------------------------------------------")
        send_email(
            subject=f"Izveštaj o novim zakonima - {date.today()}",
            message=uputstvo,
            from_addr="azure.test@positive.rs",
            to_addr="vladimir.siska@positive.rs",
            smtp_server="smtp.office365.com",
            smtp_port=587,
            username="azure.test@positive.rs",
            password=os.getenv("PRAVNIK_PASS")
            )
        print(" ")
        print("------------------------------------------------------------------------------------------------")
        print(" ")
        print("POSLAT MAIL")
        print(" ")
        print("------------------------------------------------------------------------------------------------")
    else:
        print(" ")
        print("------------------------------------------------------------------------------------------------")
        print(" ")
        print("ZAVRSENA OBRADA, SALJEM MAIL")
        print(" ")
        print("------------------------------------------------------------------------------------------------")
        send_email(
            subject=f"Izveštaj o novim zakonima - {date.today()}",
            message="NEMA NOVIH ZAKONA",
            from_addr="azure.test@positive.rs",
            to_addr="djordje.medakovic@gmail.com",
            smtp_server="smtp.office365.com",
            smtp_port=587,
            username="azure.test@positive.rs",
            password=os.getenv("PRAVNIK_PASS")
            )
        print(" ")
        print("------------------------------------------------------------------------------------------------")
        print(" ")
        print("POSLAT MAIL")
        print(" ")
        print("------------------------------------------------------------------------------------------------")
        
            
if __name__ == "__main__":
    main()
