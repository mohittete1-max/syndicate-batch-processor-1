def find_match_id_by_name(match_name: str, matches_list: list) -> str:
  """Matches local fixture name to API match title using a Syndicate Dictionary."""
  
  # Syndicate translation dictionary
  team_map = {
      "SA": "south africa",
      "NAM": "namibia",
      "SCO": "scotland",
      "NED": "netherlands",
      "THA": "thailand",
      "HK": "hong kong",
      "ADF": "amsterdam",
      "ECR": "edinburgh",
      "W": "women"
  }

  tokens = [t for t in match_name.split("_") if t.lower() != "vs"]
  expanded_tokens = [team_map.get(t.upper(), t.lower()) for t in tokens]

  best_match = None
  best_score = 0
  best_title = ""

  for m in matches_list:
    match_title = m.get("name", "").lower()
    # Count how many translated tokens exist in the API match title
    score = sum(1 for t in expanded_tokens if t in match_title)
    
    if score > best_score:
      best_score = score
      best_match = m.get("id")
      best_title = m.get("name")

  # Require at least 2 distinct tokens to match (e.g., both country names must be present)
  if best_score >= 2:
    print(f"  [API LINK] Linked '{match_name}' to live feed: '{best_title}'")
    return best_match
    
  return None
