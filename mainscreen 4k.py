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
guessed = 0
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

def checklist(input_list, check):
    resetlist = []
    
    for word in input_list:
        if word in check:
            if word not in resetlist:
                resetlist.append(word)
    
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
# Process the image
def process_image(image_path, output_path):
    
    # Open the image
    image = Image.open(image_path)
    
    # Convert to grayscale
    gray_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # Apply a threshold to binarize the image
    _, binary_image = cv2.threshold(gray_image, 190, 255, cv2.THRESH_BINARY)
    
    # Denoise the image
    #denoised_image = cv2.GaussianBlur(binary_image, (5, 5), 0)
    
    # Save the processed image
    cv2.imwrite(output_path, binary_image)    

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
    x1, x2 = 1657, 400
    y1, y2 = 738, 80
    
    # Define the region coordinates of the input field
    input_field_region = (x1, y1, x2, y2)  # Define the coordinates of the input field region

    # Take a screenshot of the input field region
    input_screenshot = take_screenshot(input_field_region)
    input_screenshot.save("champion.png")

    # Use pytesseract to perform OCR on the screenshot and extract text
    input_text = pytesseract.image_to_string(input_screenshot)
    print(input_text)

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
    global guessed
    if guessed == 0:
        x1, x2 = 1642, 400
        y1, y2 = 682, 80
    else:
        x1, x2 = 1650, 400
        y1, y2 = 832, 80
    guessed += 1
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
    
    if guessed == 0:
        gender_field = (1585, 945, 99, 99)
        position_field = (1694, 945, 99, 99)
        species_field = (1801, 945, 99, 99)
        resource_field = (1909, 945, 99, 99)
        rangetype_field = (2017, 945, 99, 99)
        regions_field = (2125, 945, 99, 99)
        year_field = (2233, 945, 99, 99)
    else:
        gender_field = (1585, 1097, 99, 99)
        position_field = (1694, 1097, 99, 99)
        species_field = (1801, 1097, 99, 99)
        resource_field = (1909, 1097, 99, 99)
        rangetype_field = (2017, 1097, 99, 99)
        regions_field = (2125, 1097, 99, 99)
        year_field = (2233, 1097, 99, 99)

    gender_screenshot = take_screenshot(gender_field)
    position_screenshot = take_screenshot(position_field)
    species_screenshot = take_screenshot(species_field)
    resource_screenshot = take_screenshot(resource_field)
    rangetype_screenshot = take_screenshot(rangetype_field)
    regions_screenshot = take_screenshot(regions_field)
    year_screenshot = take_screenshot(year_field)
    time.sleep(1)
    

    
    # Save of the screenshots taken to debug
    gender_screenshot.save("gender.png")
    position_screenshot.save("position.png")
    species_screenshot.save("species.png")
    resource_screenshot.save("resource.png")
    rangetype_screenshot.save("rangetype.png")
    regions_screenshot.save("regions.png")
    year_screenshot.save("year.png")
    
    # Process the images to make them ready for OCR
    process_image('gender.png', 'denoisedGender.png')
    process_image('position.png', 'denoisedPosition.png')
    process_image('species.png', 'denoisedSpecies.png')
    process_image('resource.png', 'denoisedResource.png')
    process_image('rangetype.png', 'denoisedRangetype.png')
    process_image('regions.png', 'denoisedRegions.png')
    process_image('year.png', 'denoisedYear.png')
    time.sleep(1)
    # Read the image
    # Gender of the champion
    gender_text = pytesseract.image_to_string('denoisedGender.png', config=custom_config)
    print('---Gender---')
    print(gender_text)
    
    # Positions of the champion
    position_text = pytesseract.image_to_string("denoisedPosition.png", config=custom_config)
    print(position_text)
    bp = position_text.strip('|')
    p = [word for word in bp.split(',') if word]
    positions = [item.strip() for item in p]
    print('---Positions---')
    print(positions)
    
    # Species of the champion
    species_text = pytesseract.image_to_string('denoisedSpecies.png', config=custom_config)
    # Cleaning up the scanned words
    clean_species_text = species_text.strip('|')
    s = [word for word in clean_species_text.split('\n') if word]
    # Connecting the species words if needed
    mbs = replace_wrong_items(s, speciescheck)
    print("---Species---")
    print(mbs)
    # Checking if the scanned str makes sense and storing the data
    lspecies = checklist(mbs,speciescheck)
    species = remove_duplicates(lspecies, speciescheck)
    
    # Which resource use the champion
    resource_text = pytesseract.image_to_string('denoisedResource.png', config=custom_config)
    # Cleaning up the read words from unnessary stuff
    clean_resource_text = [word for word in resource_text.split('\n') if word]
    checked_resource_text = replace_wrong_items(clean_resource_text, resourcescheck)
    print("---Resource---")
    print(f'{checked_resource_text}')
    # Checking if the read words are making sense and if they are valid
    lresource = checklist(checked_resource_text ,resourcescheck)
    resource = remove_duplicates(lresource, resourcescheck)
    
    # What range type does the champion use
    rangetype_text = pytesseract.image_to_string('denoisedRangetype.png', config=custom_config)
    mrangetype_text = rangetype_text.replace(',','')
    rt = [word for word in mrangetype_text.split('\n') if word]
    rangetype = [item.strip() for item in rt]
    print("---Range Type---")
    print(rangetype)
    
    #What 
    regions_text = pytesseract.image_to_string('denoisedRegions.png', config=custom_config)
    regions_text = regions_text.strip('|').strip('[')
    dr = [word for word in regions_text.split('\n') if word]
    dr_output = replace_wrong_items(dr, regionscheck)
    lregions = checklist(dr_output,regionscheck)
    regions = remove_duplicates(lregions, regionscheck)
    print('---Regions---')
    print(regions)
    
    year_text = pytesseract.image_to_string('denoisedYear.png', config=custom_config)
    print('---Year---')
    print(year_text)
    
    ig = 'gender.png'
    ip = 'position.png'
    isp = 'species.png'
    ir = 'resource.png'
    irt = 'rangetype.png'
    ire = 'regions.png'
    iy = 'year.png'
    
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
    valid_positions = checklist(positions, positioncheck)
    if valid_positions:
        
        print("Valid positions:", valid_positions)
       
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
    else:
        # Handle the case where the values are not correct
        print("Invalid positions detected. Please check the input values.")
    
    cspecies = newdetect_color(isp)
    valid_species = checklist(species, speciescheck)
    if valid_species:
        
        print("Valid species:", valid_species)
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
    else:
        # Handle the case where the values are not correct
        print("Invalid species detected. Please check the input values.")
    
    cresource = newdetect_color(ir)
    valid_resources = checklist(resource, resourcescheck)
    if valid_resources:
        print("Valid resources:", valid_resources)
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
    else:
        # Handle the case where the values are not correct
        print("Invalid resources detected. Please check the input values.")
    
    crange = newdetect_color(irt)
    valid_rangetype = checklist(rangetype, rangetypecheck)
    if valid_rangetype:
        print("Valid rangetypes:", valid_rangetype)
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
                partiallyright['range_type'] = rangetype
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
    else:
        # Handle the case where the values are not correct
        print("Invalid rangetypes detected. Please check the input values.")
    
    cregions = newdetect_color(ire)
    vaolid_regions = checklist(regions, regionscheck)
    if vaolid_regions:
        print("Valid regions:", vaolid_regions)
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
    else:
        # Handle the case where the values are not correct
        print("Invalid regions detected. Please check the input values.")
    
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

