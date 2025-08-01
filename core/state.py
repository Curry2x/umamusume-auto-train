import re

from utils.screenshot import capture_region, enhanced_screenshot
from core.ocr import extract_text, extract_number
from core.recognizer import match_template

from utils.constants import SUPPORT_CARD_ICON_REGION, MOOD_REGION, TURN_REGION, FAILURE_REGION, YEAR_REGION, MOOD_LIST, CRITERIA_REGION

# Get Stat
# STILL NOT USED
def stat_state():
  spd = enhanced_screenshot((310, 723, 55, 20))
  sta = enhanced_screenshot((405, 723, 55, 20))
  pwr = enhanced_screenshot((500, 723, 55, 20))
  guts = enhanced_screenshot((595, 723, 55, 20))
  wit = enhanced_screenshot((690, 723, 55, 20))
  spd_text = extract_number(spd)
  sta_text = extract_number(sta)
  pwr_text = extract_number(pwr)
  guts_text = extract_number(guts)
  wit_text = extract_number(wit)
  return {
    spd: spd_text,
    sta: sta_text,
    pwr: pwr_text,
    guts: guts_text,
    wit: wit_text
  }

# Check support card in each training
def check_support_card(threshold=0.8):
  SUPPORT_ICONS = {
    "spd": "assets/icons/support_card_type_spd.png",
    "sta": "assets/icons/support_card_type_sta.png",
    "pwr": "assets/icons/support_card_type_pwr.png",
    "guts": "assets/icons/support_card_type_guts.png",
    "wit": "assets/icons/support_card_type_wit.png",
    "friend": "assets/icons/support_card_type_friend.png"
  }

  count_result = {}

  for key, icon_path in SUPPORT_ICONS.items():
    matches = match_template(icon_path, SUPPORT_CARD_ICON_REGION, threshold)
    count_result[key] = len(matches)

  return count_result

# Get failure chance (idk how to get energy value)
def check_failure():
  failure = enhanced_screenshot(FAILURE_REGION)
  failure_text = extract_text(failure).lower()

  if not failure_text.startswith("failure"):
    return -1

  # SAFE CHECK
  # 1. If there is a %, extract the number before the %
  match_percent = re.search(r"failure\s+(\d{1,3})%", failure_text)
  if match_percent:
    return int(match_percent.group(1))

  # 2. If there is no %, but there is a 9, extract digits before the 9
  match_number = re.search(r"failure\s+(\d+)", failure_text)
  if match_number:
    digits = match_number.group(1)
    idx = digits.find("9")
    if idx > 0:
      num = digits[:idx]
      return int(num) if num.isdigit() else -1
    elif digits.isdigit():
      return int(digits)  # fallback

  return -1

def check_mood():
  mood = capture_region(MOOD_REGION)
  mood_text = extract_text(mood).upper()

  for known_mood in MOOD_LIST:
    if known_mood in mood_text:
      return known_mood

  print(f"[WARNING] Mood not recognized: {mood_text}")
  return "UNKNOWN"

# Check turn
def check_turn():
  turn = enhanced_screenshot(TURN_REGION)
  turn_text = extract_text(turn)
  if "Race Day" in turn_text:
    return "Race Day"
  
  # sometimes easyocr misread characters instead of numbers
  cleaned_text = (
    turn_text
    .replace("T", "1")
    .replace("I", "1")
    .replace("O", "0")
    .replace("S", "5")
  )
  if cleaned_text:
    return int(cleaned_text)
  
  return -1

# Check year
def check_current_year():
  year = enhanced_screenshot(YEAR_REGION)
  text = extract_text(year)
  return text

# Check criteria
def check_criteria():
  img = enhanced_screenshot(CRITERIA_REGION)
  text = extract_text(img)
  return text