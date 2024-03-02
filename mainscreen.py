import pyautogui
from PIL import Image
import pytesseract
import time
import cv2
import json
from difflib import get_close_matches
import numpy as np
import random
import re

tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = tesseract_path

# Initialize an empty list to store the champions' information
champions_list = []
# Citeria that was orange
otherp = ''
othersp = ''
otherrs = ''
otherrt = ''
otherr = ''
criteria = {
    'gender': '',
    'positions':'',
    'species': '',
    'resource': '',
    'range_type': '',
    'regions': '',
    'release_year': ''
    }
anticriteria = {
    'name' : '',
    'gender': '',
    'positions':'',
    'species': '',
    'resource': '',
    'range_type': '',
    'regions': '',
    'release_year': ''
    }
tried_names = []
# Set the language
custom_config = r'--oem 3 --psm 6 -l loldle'
# Checklists
regionscheck = ['Ixtal','Icathia','Runeterra', "Piltover", "Noxus", "Shadow Isles", "Zaun", "Targon", "Bandle City", "Void", "Shurima", "Freljord", "Ionia", 'Bilgewater','Camavor','Demacia']
resourcescheck = ['Flow','Bloodthirst','Grit','Heat','Ferocity','Rage','Shield','Courage','Fury', 'Mana', 'Manaless', 'Healthcosts', 'Energy']
speciescheck = ['Cat','Brackern','Revenant','Vastayan','Dog','Rat','Troll','Unknown','Undead','Human','Magically Altered', 'Yordle', 'Golem', 'Magicborn', 'Demon', 'Spirit', 'Chemically Altered', 'Aspect', 'Void-Being', 'Cyborg', 'Iceborn', 'Celestial', 'God-Warrior', 'Dragon', 'Spiritualist', 'God','Darkin']
positioncheck = ['Middle','Top','Jungle','Bottom','Support']
# Function to add a champion to the list if it doesn't already exist
def add_champion(name, gender, positions, species, resource, range_type, regions, release_year):
    with open('champions.json', 'r') as f:
        champions_list = json.load(f)

    for champion in champions_list:
        if champion['name'] == name:
            print("Champion already exists, no need to add")
            return

    # Champion not found, add it to the list
    champions_list.append({
        'name': name,
        'gender': gender,
        'positions': positions,
        'species': species,
        'resource': resource,
        'range_type': range_type,
        'regions': regions,
        'release_year': release_year
    })

    # Write the updated champions_list back to the JSON file
    with open('champions.json', 'w') as f:
        json.dump(champions_list, f, indent=4)
# Check function to check two different outputs 
def checkliste(list1, list2, check):
    resetlist = []
    x = list1
    y = list2
    
    for word in x:
        if word in check:
            #print(f"{word} exists in the checklist")
            resetlist.append(word)
            #print(resetlist)
        else:
           pass #print(f"{word} doesn't exists in the checklist")
    for word in y:
        if word in check:
            #print(f"{word} exists in the checklist")
            if word in resetlist:
                pass #print("Already in the list")
            else:
                resetlist.append(word)
                pass #print(resetlist)
        else:
            pass
            #print(f"{word} doesn't exists in the checklist")
    return resetlist
# Color detection
def newdetect_color(image):
    # Load the image
    image = cv2.imread(image)
    
    # Convert the image to the HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Define color ranges in HSV format
    green_lower = np.array([40, 40, 40])  # Lower HSV values for green
    green_upper = np.array([80, 255, 255]) # Upper HSV values for green
    
    red_lower1 = np.array([0, 100, 100])   # Lower HSV values for red (part 1)
    red_upper1 = np.array([10, 255, 255])  # Upper HSV values for red (part 1)
    red_lower2 = np.array([170, 100, 100]) # Lower HSV values for red (part 2)
    red_upper2 = np.array([180, 255, 255]) # Upper HSV values for red (part 2)
    
    orange_lower = np.array([10, 100, 100]) # Lower HSV values for orange
    orange_upper = np.array([25, 255, 255]) # Upper HSV values for orange
    
    # Create masks for each color range
    green_mask = cv2.inRange(hsv_image, green_lower, green_upper)
    red_mask1 = cv2.inRange(hsv_image, red_lower1, red_upper1)
    red_mask2 = cv2.inRange(hsv_image, red_lower2, red_upper2)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)
    orange_mask = cv2.inRange(hsv_image, orange_lower, orange_upper)
    
    # Check if any of the masks have non-zero pixels
    if np.any(green_mask):
        return "Green"
    elif np.any(red_mask):
        return "Red"
    elif np.any(orange_mask):
        return "Orange"
    else:
        return "No color found"
# Function to take a screenshot of a specific area
def take_screenshot(region):
    screenshot = pyautogui.screenshot(region=region)
    return screenshot
# To sort out wrong inputs from the image reading
def replace_wrong_items(input_list, available_list):
    output_list = []
    for item in input_list:
        # Check if the item is in the available list
        if 'God-' in item:
            output_list.append('God-Warrior')
        elif 'Health' in item:
            output_list.append('Healthcosts')
        else:    
            if item in available_list:
                output_list.append(item)
            else:
            # Check for close matches using get_close_matches
                matches = get_close_matches(item, available_list)
                if matches:
                # If a close match is found, append the closest match to the output list
                    output_list.append(matches[0])
                else:
                # If no close match is found, drop the item from the output list
                    pass
    return output_list
# Check if there are duplicates and if remove them
def remove_duplicates(input_list, available_check):
    # Convert the input list to a set to remove duplicates
    unique_lists = set(input_list)
    
    # Check if the unique regions are all valid regions/species/resources
    valid_lists = [list for list in unique_lists if list in available_check]
    
    # Return the list of valid, unique regions
    return valid_lists
# Make the first guess
def make_first_guess(guess):
    global tried_names
    x1, x2 = 1660, 400
    y1, y2 = 620, 80
    
    # Define the region coordinates of the input field
    input_field_region = (x1, y1, x2, y2)  # Define the coordinates of the input field region

    # Take a screenshot of the input field region
    input_screenshot = take_screenshot(input_field_region)
    input_screenshot.save("champion.png")

    # Use pytesseract to perform OCR on the screenshot and extract text
    input_text = pytesseract.image_to_string(input_screenshot)

    # Write "Nasus" into the input field if it's empty
    if  input_text.strip() == 'Type champion name ...' or input_text.strip() == 'Type champion name...':
        # Click on the input field (adjust the coordinates as needed)
        pyautogui.click(x1 + 250, y1 + 30)
        tried_names.append([guess])
        # Type "Nasus" into the input field
        pyautogui.typewrite(guess)
        time.sleep(1)  # Wait for typing to complete

        # Press Enter to confirm the input
        pyautogui.press('enter')
        
        pyautogui.click(x1 - 100, y1)

    # Wait for some time for the answer (adjust as needed)
    time.sleep(5)
    
    latestresults()
# Make guesses
def make_guess(guess):
    x1, x2 = 1650, 400
    y1, y2 = 715, 80
    # Define the region coordinates of the input field
    input_field_region = (x1, y1, x2, y2)  # Define the coordinates of the input field region

    # Take a screenshot of the input field region
    input_screenshot = take_screenshot(input_field_region)
    input_screenshot.save("champion2.png")

    # Use pytesseract to perform OCR on the screenshot and extract text
    input_text = pytesseract.image_to_string(input_screenshot)

    # Write "Nasus" into the input field if it's empty
    if  input_text.strip() == 'Type champion name ...' or input_text.strip() == 'Type champion name...':
        # Click on the input field (adjust the coordinates as needed)
        pyautogui.click(x1 + 300, y1 + 30)

        # Type "Nasus" into the input field
        pyautogui.typewrite(guess)
        time.sleep(1)  # Wait for typing to complete

        # Press Enter to confirm the input
        pyautogui.press('enter')
        pyautogui.click(x1 - 100, y1)
    # Wait for some time for the answer (adjust as needed)
    time.sleep(5)
    
    latestresults()
# Check the latest search    
def latestresults():
    global otherp, otherr, otherrs, othersp, otherrt, criteria, anticriteria, tried_names
    print(otherp, otherr, otherrs, otherrt, othersp)
    print('--Tried names--')
    print(tried_names)
    #swait = input("Can I continue ?")
    # Define the region coordinates of the input field
    input_field_region = (1450, 890, 900, 200)  # Define the coordinates of the input field region

    # Take a screenshot of the input field region
    input_screenshot = take_screenshot(input_field_region)
    
    input_screenshot.save("screenshot.png")
    gender_field = (1580, 980, 100, 95)
    gender_screenshot = take_screenshot(gender_field)
    position_field = (1687, 980, 100, 95)
    position_screenshot = take_screenshot(position_field)
    species_field = (1795, 970, 108, 108)
    species_screenshot = take_screenshot(species_field)
    resource_field = (1908, 980, 105, 95)
    resource_screenshot = take_screenshot(resource_field)
    rangetype_field = (2013, 980, 100, 95)
    rangetype_screenshot = take_screenshot(rangetype_field)
    regions_field = (2120, 970, 105, 105)
    regions_screenshot = take_screenshot(regions_field)
    year_field = (2228, 980, 100, 95)
    year_screenshot = take_screenshot(year_field)
    
    # Save of the screenshots taken to debug
    gender_screenshot.save("gender.png")
    position_screenshot.save("position.png")
    species_screenshot.save("species.png")
    resource_screenshot.save("resource.png")
    rangetype_screenshot.save("rangetype.png")
    regions_screenshot.save("regions.png")
    year_screenshot.save("year.png")
    ig = 'gender.png'
    ip = 'position.png'
    isp = 'species.png'
    ir = 'resource.png'
    irt = 'rangetype.png'
    ire = 'regions.png'
    iy = 'year.png'
    # Read the image
    species_image = cv2.imread('species.png', cv2.IMREAD_GRAYSCALE)
    resource_image = cv2.imread('resource.png', cv2.IMREAD_GRAYSCALE)
    regions_image = cv2.imread('regions.png', cv2.IMREAD_GRAYSCALE)

    # Apply Gaussian blur for denoising
    denoised_s_image = cv2.GaussianBlur(species_image, (5, 5), 0)
    denoised_r_image = cv2.GaussianBlur(resource_image, (5, 5), 0)
    denoised_rs_image = cv2.GaussianBlur(regions_image, (5, 5), 0)
    cv2.imwrite('denoised_s_image.png', denoised_s_image)
    cv2.imwrite('denoised_r_image.png', denoised_r_image)
    cv2.imwrite('denoised_rs_image.png', denoised_rs_image)
    
    
    # Apply binary thresholding
    _, binarized_r_image = cv2.threshold(resource_image, 190, 255, cv2.THRESH_BINARY)
    _, binarized_s_image = cv2.threshold(species_image, 190, 255, cv2.THRESH_BINARY)
    _, binarized_rs_image = cv2.threshold(regions_image, 190, 255, cv2.THRESH_BINARY)

    cv2.imwrite('binarized_r_image.png', binarized_r_image)
    cv2.imwrite('binarized_s_image.png', binarized_s_image)
    cv2.imwrite('binarized_rs_image.png', binarized_rs_image)

    # Use pytesseract to perform OCR on the screenshot and extract text
    input_text = pytesseract.image_to_string(input_screenshot)
    #gender of the champion
    gender_text = pytesseract.image_to_string(gender_screenshot)
    #positions of the champion
    position_text = pytesseract.image_to_string(position_screenshot)
    bp = position_text.strip('|')
    p = [word for word in bp.split(',') if word]
    positions = [item.strip() for item in p]
    print('---Positions---')
    print(positions)
    #species of the champion
    bspecies_text = pytesseract.image_to_string(binarized_s_image, config=custom_config)
    dspecies_text = pytesseract.image_to_string(denoised_s_image, config=custom_config)
    #Cleaning up the scanned words
    bspecies = bspecies_text.strip('|')
    dspecies = dspecies_text.strip('|')
    s = [word for word in bspecies.split('\n') if word]
    t = [word for word in dspecies.split('\n') if word]
    #Connecting the species words if needed
    mbs = replace_wrong_items(s, speciescheck)
    mds = replace_wrong_items(t, speciescheck)
    #removing the commas in the list
    print("---Species---")
    print(mbs)
    print(mds)
    #checking if the scanned str makes sense and storing the data
    lspecies = checkliste(mbs,mds,speciescheck)
    species = remove_duplicates(lspecies, speciescheck)
        
    #Which resource use the champion
    bresource_text = pytesseract.image_to_string(binarized_r_image, config=custom_config)
    dresource_text = pytesseract.image_to_string(denoised_r_image, config=custom_config)
    #cleaning up the read words from unnessary stuff
    drr = [word for word in dresource_text.split('\n') if word]
    brr = [word for word in bresource_text.split('\n') if word]
    drx = replace_wrong_items(drr, resourcescheck)
    brx = replace_wrong_items(brr, resourcescheck)
    print("---Recource---")
    print(f'{drx}')
    print(f'{brx}')
    #checking if the read words are making sense and if they are valid
    lresource = checkliste(drx,brx,resourcescheck)
    resource = remove_duplicates(lresource, resourcescheck)
    #what range type does the champion use
    rangetype_text = pytesseract.image_to_string(rangetype_screenshot)
    mrangetype_text = rangetype_text.replace(',','')
    rt = [word for word in mrangetype_text.split('\n') if word]
    rangetype = [item.strip() for item in rt]
    
    #What 
    bregions_text = pytesseract.image_to_string(binarized_rs_image, config=custom_config)
    dregions_text = pytesseract.image_to_string(denoised_rs_image, config=custom_config)
    bregions = bregions_text.strip('|').strip('[')
    dregions = dregions_text.strip('|').strip('[')
    #mregions_text = bregions.replace(',','')
    dr = [word for word in dregions.split('\n') if word]
    br = [word for word in bregions.split('\n') if word]
    dr_output = replace_wrong_items(dr, regionscheck)
    br_output = replace_wrong_items(br, regionscheck)
    lregions = checkliste(dr_output,br_output,regionscheck)
    regions = remove_duplicates(lregions, regionscheck)
    print('---Regions---')
    print(regions)
    
    year_text = pytesseract.image_to_string(year_screenshot)
    #add_champion(name, gender_text.strip(),positions,species,resource,rangetype,regions,year_text.strip())
    
    cgender = newdetect_color(ig)
    if cgender == 'Green':
        criteria['gender'] = [gender_text.strip()]
    else:
        if len(anticriteria.get('gender', [])) >= 1:
            if [gender_text.strip()] not in anticriteria['gender']:
                anticriteria['gender'].append(gender_text.strip())
            else:
                pass
        else: 
            anticriteria['gender'] = [gender_text.strip()]
        pass
    
    cpositions = newdetect_color(ip)
    if cpositions == 'Green':
        criteria['positions'] = positions
    elif cpositions == 'Orange':
        if len(criteria.get('positions', [])) == 0 :
            criteria['positions'] = [positions[0]]
            if len(positions) > 2:
                otherp = [positions[1], positions[2]]
            elif len(positions) == 2:
                otherp = [positions[1]]
        else:
            criteria['positions'] = otherp
    else:
        if len(anticriteria.get('positions', [])) >= 1:
            if positions not in anticriteria['positions']:
                anticriteria['positions'].append(positions)
                flatpositions = flatten(anticriteria['positions'])
                anticriteria['positions'] = flatpositions
            else:
                pass
        else: 
            anticriteria['positions'] = positions
        pass  
    
    cspecies = newdetect_color(isp)
    if cspecies == 'Green':
        criteria['species'] = species            
    elif cspecies == 'Orange':
        if len(criteria.get('species', [])) == 0: 
            criteria['species'] = [species[0]]
            if len(species) > 2: 
                othersp = [species[1], species[2]]
            elif len(species) == 2:
                othersp = [species[1]]
        else:
            criteria['species'] = othersp
    else:
        if len(anticriteria.get('species', [])) >= 1:
            if species not in anticriteria['species']:
                anticriteria['species'].append(species)
                flatspecies = flatten(anticriteria['species'])
                anticriteria['species'] = flatspecies
            else:
                pass
        else: 
            anticriteria['species'] = species
        pass
    
    cresource = newdetect_color(ir)
    if cresource == 'Green':
        criteria['resource'] = resource       
    elif cresource == 'Orange':
        if len(criteria.get('resource',[])) == 0:
            criteria['resource'] = resource[0]
            if len(resource) > 2:
                otherrs = [resource[1], resource[2]]
            elif len(resource) == 2 :
                otherrs = [resource[1]]
        else:
            criteria['resource'] = otherrs
    else:
        if len(anticriteria.get('resource',[])) >= 1:
            if resource not in anticriteria['resource']:
                anticriteria['resource'].append(resource)
                flatresource = flatten(anticriteria['resource'])
                anticriteria['resource'] = flatresource
            else:
                pass
        else: 
            anticriteria['resource'] = resource
        pass
    
    crange = newdetect_color(irt)
    if crange == 'Green':
        criteria['range_type'] = rangetype
    elif crange == 'Orange':
        if len(criteria.get('range_type', [])) == 0:
            criteria['range_type'] = [rangetype[0]]
            if len(rangetype) > 2:
                otherrt = [rangetype[1],rangetype[2]]
            elif len(rangetype) == 2:
                otherrt = [rangetype[1]]
        else:
            criteria['range_type'] = otherrt
    else:
        if len(anticriteria.get('range_type', [])) >= 1:
            if rangetype not in anticriteria['range_type']:
                anticriteria['range_type'].append(rangetype)
                flatrangetype = flatten(anticriteria['range_type'])
                anticriteria['range_type'] = flatrangetype
            else:
                pass
        else:  
            anticriteria['range_type'] = rangetype
        pass
    
    cregions = newdetect_color(ire)
    if cregions == 'Green':
        criteria['regions'] = regions
    elif cregions == 'Orange':
        if len(criteria.get('regions', [])) == 0:
            criteria['regions'] = [regions[0]]
            if len(regions) > 2:
                otherr = [regions[1],regions[2]]
            elif len(regions) == 2:
                otherr = [regions[1]]
        else:
            criteria['regions'] = otherr
    else:
        if len(anticriteria.get('regions', [])) >= 1:
            if regions not in anticriteria['regions']:
                anticriteria['regions'].append(regions)
                flatregions = flatten(anticriteria['regions'])
                anticriteria['regions'] = flatregions
            else:
                pass
        else:
            anticriteria['regions'] = regions
        pass
    
    cyear = newdetect_color(iy)
    if cyear == 'Green':
        criteria['release_year'] = [year_text.strip()]
    else:
        if len(anticriteria.get('release_year', [])) >= 1:
            if [year_text.strip()] not in anticriteria['release_year']:
                anticriteria['release_year'].append(year_text.strip())
            else:
                pass
        else:
            anticriteria['release_year'] = [year_text.strip()]
        pass
    
    anticriteria['positions'] = list(set(anticriteria['positions']))
    anticriteria['regions'] = list(set(anticriteria['regions']))
    anticriteria['species'] = list(set(anticriteria['species']))
    anticriteria['release_year'] = list(set(anticriteria['release_year']))
    print(criteria)
    # Cleans the criteria list from empty spaces, so that we can search for a champion in the list
    criteria = {key: value for key, value in criteria.items() if value != '' and value != ['']}
    anticriteria = {key: value for key, value in anticriteria.items() if value != '' and value != ['']}
    print(f'This is the current search criteria:{criteria}')
    print(f'This is the current wrong criteria:{anticriteria}')       
    
   
    
    
    with open('champions.json', 'r') as f:
        champions_list = json.load(f)
    # New guess will be generated from a list of characters
    newguess = search_champions(champions_list, criteria, anticriteria, tried_names)
    newguess = flatten(newguess)
    print(newguess)
    if len(newguess) > 1:
        number = random.randrange(0,len(newguess),1)
        
        if len(tried_names) == 0: 
            tried_names.append([newguess[number]])
            make_guess(newguess[number])
        else:
            tried_names.append([newguess[number]])
            make_guess(newguess[number])
    elif len(newguess) == 1:
        if len(tried_names) == 0:
            tried_names.append([newguess[0]])
            make_guess(newguess[0])
        else:
            tried_names.append([newguess[0]])
            make_guess(newguess[0])
    else:
        print('There was no matching character')
        time.sleep(2)
        latestresults()
    
    
 
    

    time.sleep(3)
    champions_list.clear()
    return 
# Search for champions that fit the criteria
def search_champions(champions, criteria, anticriteria, tried_names):
    matching_champions = []
    for champion in champions:
        # Check if champion matches any condition in the anticriteria
        if any(champion.get(key) == value for key, value in anticriteria.items()):
                continue  # Skip this champion if it matches any anticriteria condition
        # Check if champion matches the criteria
        if all(champion.get(key) == value for key, value in criteria.items()):
            matching_champions.append(champion['name'])
    # Filter out already tried names
    matching_champions = [champion for champion in matching_champions if champion not in tried_names]
    return matching_champions
# Flatten the lists as sublists appear
def flatten(lst):
    flattened = []
    for item in lst:
        if isinstance(item, list):
            flattened.extend(flatten(item))
        elif item != '':
            flattened.append(item)
    return flattened
# Get a random champion 
def get_random_champion():
    # Load champion data from JSON file
    with open('champions.json', 'r') as f:
        champions_list = json.load(f)

    # Extract the list of champion names from the loaded data
    champion_names = [champion['name'] for champion in champions_list]

    # Get a random champion name
    champion = random.choice(champion_names)
    champion = champion[0]
    champion = re.sub(r"\[|\]", "", champion)
    
    return champion

guess = get_random_champion()

make_first_guess(guess)

