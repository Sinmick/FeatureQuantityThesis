import requests
import csv
import time
import datetime
api_key = "45cd34a57c5920aecab91f4a1933b903"


#urlPopular = f"https://libraries.io/api/search?platforms=PyPI&sort=rank&order=desc&page={page}&api_key={api_key}"
#urlMostUsed = f"https://libraries.io/api/search?platforms=PyPI&sort=dependent_repos_count&order=desc&page={page}&api_key={api_key}"
#responseP = requests.get(urlPopular)
#packagesP = responseP.json()
#responseM = requests.get(urlMostUsed)
#packagesM = responseM.json()

with open('rawbenignpackages.csv', 'w', newline='') as csvfile:
    fieldname = ['Package Name', 'Source Rank', 'Forks', 'Dependents Count', 'Dependent Repos Count', 'Stars', 'Contributions', 'Repository URL', 'Latest release version', 'First release', 'Download URL', 'Language', 'Platform']
    writer = csv.DictWriter(csvfile, fieldnames=fieldname)
    writer.writeheader()
    for pageNum in range(150):
        urlPopular = f"https://libraries.io/api/search?platforms=PyPI&sort=rank&order=desc&page={pageNum}&api_key={api_key}"
        urlMostUsed = f"https://libraries.io/api/search?platforms=PyPI&sort=dependent_repos_count&order=desc&page={pageNum}&api_key={api_key}"
        try:
            responseP = requests.get(urlPopular)
            packagesP = responseP.json()
            responseM = requests.get(urlMostUsed)
            packagesM = responseM.json()
        except Exception as e:
            print(f"Failed to download package info:{e}")
        for package in packagesP:
            EarliestDT = datetime.datetime.now()
            for version in package["versions"]:
                published_at_str = version["published_at"]
                published_at_dt = datetime.datetime.strptime(published_at_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                if(published_at_dt < EarliestDT):
                    EarliestDT = published_at_dt
            
            writer.writerow({
                'Package Name': package['name'],
                'Source Rank': package['rank'],
                'Forks': package['forks'],
                'Dependents Count': package['dependents_count'],
                'Stars': package['stars'],
                'Platform': package['platform'],
                'Language': package['language'],
                'Dependent Repos Count': package['dependent_repos_count'],
                'Contributions': package['contributions_count'],
                'Repository URL': package['repository_url'],
                'Latest release version': package['latest_release_number'],
                'Download URL': package['latest_download_url'],
                'First release': EarliestDT
            })
        for package in packagesM:
            EarliestDT = datetime.datetime.now()
            for version in package["versions"]:
                published_at_str = version["published_at"]
                published_at_dt = datetime.datetime.strptime(published_at_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                if(published_at_dt < EarliestDT):
                    EarliestDT = published_at_dt
            writer.writerow({
                'Package Name': package['name'],
                'Source Rank': package['rank'],
                'Forks': package['forks'],
                'Dependents Count': package['dependents_count'],
                'Stars': package['stars'],
                'Platform': package['platform'],
                'Language': package['language'],
                'Dependent Repos Count': package['dependent_repos_count'],
                'Contributions': package['contributions_count'],
                'Repository URL': package['repository_url'],
                'Latest release version': package['latest_release_number'],
                'Download URL': package['latest_download_url'],
                'First release': EarliestDT
            })
        print("Successfull write to CSV file")
        #time.sleep(1)

    for pageN in range(100):
        urlStars = f"https://libraries.io/api/search?platforms=PyPI&sort=stars&order=desc&page={pageN}&api_key={api_key}"
        urlContributions = f"https://libraries.io/api/search?platforms=PyPI&sort=contributions_count&order=desc&page={pageN}&api_key={api_key}"
        urlRelevance = f"https://libraries.io/api/search?platforms=PyPI&order=desc&page={pageN}&api_key={api_key}"
        urlDependents = f"https://libraries.io/api/search?platforms=PyPI&sort=dependents_count&order=desc&page={pageN}&api_key={api_key}"
        try:
            responseStars = requests.get(urlStars)
            packagesStars = responseStars.json()
            responseContributions = requests.get(urlContributions)
            packagesContributions = responseContributions.json()
            responseRelevance = requests.get(urlRelevance)
            packagesRelevance = responseRelevance.json()
            responseDependent = requests.get(urlDependents)
            packagesDependent = responseDependent.json()
        except Exception as e:
            print(f"Failed to download package info:{e}")
        for package in packagesStars:
            EarliestDT = datetime.datetime.now()
            for version in package["versions"]:
                published_at_str = version["published_at"]
                published_at_dt = datetime.datetime.strptime(published_at_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                if(published_at_dt < EarliestDT):
                    EarliestDT = published_at_dt
            writer.writerow({
                'Package Name': package['name'],
                'Source Rank': package['rank'],
                'Forks': package['forks'],
                'Dependents Count': package['dependents_count'],
                'Stars': package['stars'],
                'Platform': package['platform'],
                'Language': package['language'],
                'Dependent Repos Count': package['dependent_repos_count'],
                'Contributions': package['contributions_count'],
                'Repository URL': package['repository_url'],
                'Latest release version': package['latest_release_number'],
                'Download URL': package['latest_download_url'],
                'First release': EarliestDT
            })
        for package in packagesContributions:
            EarliestDT = datetime.datetime.now()
            for version in package["versions"]:
                published_at_str = version["published_at"]
                published_at_dt = datetime.datetime.strptime(published_at_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                if(published_at_dt < EarliestDT):
                    EarliestDT = published_at_dt
            writer.writerow({
                'Package Name': package['name'],
                'Source Rank': package['rank'],
                'Forks': package['forks'],
                'Dependents Count': package['dependents_count'],
                'Stars': package['stars'],
                'Platform': package['platform'],
                'Language': package['language'],
                'Dependent Repos Count': package['dependent_repos_count'],
                'Contributions': package['contributions_count'],
                'Repository URL': package['repository_url'],
                'Latest release version': package['latest_release_number'],
                'Download URL': package['latest_download_url'],
                'First release': EarliestDT
            })
        for package in packagesRelevance:
            EarliestDT = datetime.datetime.now()
            for version in package["versions"]:
                published_at_str = version["published_at"]
                published_at_dt = datetime.datetime.strptime(published_at_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                if(published_at_dt < EarliestDT):
                    EarliestDT = published_at_dt
            writer.writerow({
                'Package Name': package['name'],
                'Source Rank': package['rank'],
                'Forks': package['forks'],
                'Dependents Count': package['dependents_count'],
                'Stars': package['stars'],
                'Platform': package['platform'],
                'Language': package['language'],
                'Dependent Repos Count': package['dependent_repos_count'],
                'Contributions': package['contributions_count'],
                'Repository URL': package['repository_url'],
                'Latest release version': package['latest_release_number'],
                'Download URL': package['latest_download_url'],
                'First release': EarliestDT
            })
        for package in packagesDependent:
            EarliestDT = datetime.datetime.now()
            for version in package["versions"]:
                published_at_str = version["published_at"]
                published_at_dt = datetime.datetime.strptime(published_at_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                if(published_at_dt < EarliestDT):
                    EarliestDT = published_at_dt
            writer.writerow({
                'Package Name': package['name'],
                'Source Rank': package['rank'],
                'Forks': package['forks'],
                'Dependents Count': package['dependents_count'],
                'Stars': package['stars'],
                'Platform': package['platform'],
                'Language': package['language'],
                'Dependent Repos Count': package['dependent_repos_count'],
                'Contributions': package['contributions_count'],
                'Repository URL': package['repository_url'],
                'Latest release version': package['latest_release_number'],
                'Download URL': package['latest_download_url'],
                'First release': EarliestDT
            })
        print("Successfull write to CSV file")
        #time.sleep(1)