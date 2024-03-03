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
partiallyright = {
    'positions':'',
    'species': '',
    'resource': '',
    'range_type': '',
    'regions': '',
    }
tried_names = []
# Set the language
custom_config = r'--oem 3 --psm 6 -l loldle'
# Checklists
regionscheck = ['Ixtal','Icathia','Runeterra', "Piltover", "Noxus", "Shadow Isles", "Zaun", "Targon", "Bandle City", "Void", "Shurima", "Freljord", "Ionia", 'Bilgewater','Camavor','Demacia']
resourcescheck = ['Flow','Bloodthirst','Grit','Heat','Ferocity','Rage','Shield','Courage','Fury', 'Mana', 'Manaless', 'Healthcosts', 'Energy']
speciescheck = ['Cat','Brackern','Revenant','Vastayan','Dog','Rat','Troll','Unknown','Undead','Human','Magically Altered', 'Yordle', 'Golem', 'Magicborn', 'Demon', 'Spirit', 'Chemically Altered', 'Aspect', 'Void-Being', 'Cyborg', 'Iceborn', 'Celestial', 'God-Warrior', 'Dragon', 'Spiritualist', 'God','Darkin']
positioncheck = ['Middle','Top','Jungle','Bottom','Support']
rangetypecheck = ['Meele', 'Ranged']
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
    global  criteria, anticriteria, tried_names, partiallyright
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
        if len(partiallyright.get('positions', [])) >= 1:
            if positions not in partiallyright['positions']:
                partiallyright['positions'].append(positions)
                flattenpositions = flatten(partiallyright['positions'])
                partiallyright['positions'] = flattenpositions
                partiallyright['positions'] = remove_duplicates(partiallyright['positions'], positioncheck)
            else:
                pass
        else: 
            partiallyright['positions'] = positions
        pass
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
        if len(partiallyright.get('species', [])) >= 1:
            if species not in partiallyright['species']:
                partiallyright['species'].append(species)
                flattenspecies = flatten(partiallyright['species'])
                partiallyright['species'] = flattenspecies
                partiallyright['species'] = remove_duplicates(partiallyright['species'], speciescheck)
            else:
                pass
        else: 
            partiallyright['species'] = species
        pass
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
        if len(partiallyright.get('resource', [])) >= 1:
            if resource not in partiallyright['resource']:
                partiallyright['resource'].append(resource)
                flattenresource = flatten(partiallyright['resource'])
                partiallyright['resource'] = flattenresource
                partiallyright['resource'] = remove_duplicates(partiallyright['resource'], resourcescheck)
            else:
                pass
        else: 
            partiallyright['resource'] = resource
        pass
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
        if len(criteria.get('range_type', [])) >= 1:
            if rangetype not in partiallyright['range_type']:
                partiallyright['range_type'].append(rangetype)
                flattenrangetype = flatten(partiallyright['range_type'])
                partiallyright['range_type'] = flattenrangetype
                partiallyright['range_type'] = remove_duplicates(partiallyright['range_type'], rangetypecheck)
            else:
                pass
        else:
          partiallyright['range_type']  = rangetype
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
        if len(partiallyright.get('regions', [])) >= 1:
            if regions not in partiallyright['regions']:
                partiallyright['regions'].append(regions)
                flattenregions = flatten(partiallyright['regions'])
                partiallyright['regions'] = flattenregions
                partiallyright['regions'] = remove_duplicates(partiallyright['regions'], regionscheck)
            else:
                pass
        else: 
            partiallyright['regions'] = regions
        pass
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
    # Cleaning up the lists from dublications
    
    
    
    
    
    
    # Cleans the criteria list from empty spaces, so that we can search for a champion in the list
    criteria = {key: value for key, value in criteria.items() if value != '' and value != ['']}
    anticriteria = {key: value for key, value in anticriteria.items() if value != '' and value != ['']}
    print(f'This is the current search criteria:{criteria}')
    print(f'This is the current wrong criteria:{anticriteria}')
    print(f'This is the current partially right criteria: {partiallyright}')       
    
    partiallyright = {key: value for key, value in partiallyright.items() if value != '' and value != [''] and value != []}
    
    
    with open('champions.json', 'r') as f:
        champions_list = json.load(f)
    # New guess will be generated from a list of characters
    partiallyrightchamps = filter_partially_correct_champions(champions_list, partiallyright, criteria)
    newguess = search_champions(champions_list, criteria, anticriteria, partiallyright, tried_names)
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
def search_champions(all_champions, criteria, anticriteria, partially_right_criteria, tried_names):
    matching_champions = []
    for champion in all_champions:
        if champion['name'] in tried_names:
            continue  # Skip if the champion has already been tried
        if match_criteria(champion, criteria) and not match_anticriteria(champion, anticriteria):
            # Check if the champion also matches the partially right criteria
            if match_partially_right_criteria(champion, partially_right_criteria):
                matching_champions.append(champion['name'])
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
# Check for champions that are partially correct
def filter_partially_correct_champions(champions, partially_criteria, criteria):
    partially_correct_champions = []
    for champion in champions:
        is_partially_correct = False
        for key, values in partially_criteria.items():
            if key in champion and any(value in champion[key] for value in values):
                is_partially_correct = True
                break
        if is_partially_correct:
            # Check if the champion also matches the normal criteria and contains at least one of the items from the keys
            if all(champion.get(key) == value for key, value in criteria.items()) and any(key in champion for key in partially_criteria.keys()):
                partially_correct_champions.append(champion)
    return partially_correct_champions

def match_criteria(champion, criteria):
    for key, values in criteria.items():
        if key in champion:
            # Ensure that the values in the champion's attribute match the criteria
            champion_values = set(champion[key])
            if not set(values).issubset(champion_values):
                return False
        else:
            # If the key is not in the champion's attributes, it does not match the criteria
            return False
    return True

def match_anticriteria(champion, anticriteria):
    for key, values in anticriteria.items():
        if key in champion:
            # Check if any value in the champion's attribute matches any value in anticriteria
            if any(value in champion[key] for value in values):
                return True
    return False

def match_partially_right_criteria(champion, partially_right_criteria):
    for key, values in partially_right_criteria.items():
        if key in champion:
            # Ensure that the intersection between the champion's attribute and values for the key is not empty
            if not set(champion[key]).intersection(values):
                return False
    return True

guess = get_random_champion()

make_first_guess(guess)

