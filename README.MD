mkdir coba-install  
python -m venv venv    
Set-ExecutionPolicy Unrestricted -Scope Process
            # ingin matiin
            Set-ExecutionPolicy Restricted -Scope Process
            
 .\venv\Scripts\activate
pip install scrapy
scrapy startproject bookscraper