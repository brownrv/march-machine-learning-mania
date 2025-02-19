import pandas as pd
import re

def extract_game_info(id_str: str) -> tuple[int, int, int]:
    """
    Extract season and team IDs from a Kaggle competition game ID string.

    Args:
        id_str (str): The game ID string formatted as "YYYY_Team1_Team2".
    
    Returns:
        tuple[int, int, int]: A tuple containing (Season, TeamID1, TeamID2).
    """
    try:
        year, team1, team2 = map(int, id_str.split('_'))
        return year, team1, team2
    except ValueError:
        raise ValueError(f"Unexpected ID format: {id_str}")

### Example usage:
# # Load the sample submission file
# submission_df = pd.read_csv('/mnt/data/SampleSubmissionStage1.csv')

# # Extract game info into new columns
# submission_df[['Season', 'TeamID1', 'TeamID2']] = submission_df['ID'].apply(extract_game_info).apply(pd.Series)


def extract_seed_value(seed_str: str) -> int:
    """
    Extracts the numeric seed value from an NCAA tournament seed string.

    Args:
        seed_str (str): The seed string (e.g., 'W01', 'Y12b').

    Returns:
        int: The extracted seed value, or 16 if extraction fails.
    """
    try:
        # Extract numeric part using regex
        match = re.search(r'\d+', seed_str)
        if match:
            return int(match.group())
        else:
            return 16  # Default seed value for unselected teams/errors
    except (ValueError, TypeError):
        return 16  # Default for unexpected cases

### Example usage:
# # Load the tournament seed data
# w_seed = pd.read_csv('/mnt/data/WNCAATourneySeeds.csv')
# m_seed = pd.read_csv('/mnt/data/MNCAATourneySeeds.csv')

# # Concatenate men's and women's data
# seed_df = pd.concat([m_seed, w_seed], axis=0, ignore_index=True)

# # Apply the function to extract seed values
# seed_df['SeedValue'] = seed_df['Seed'].apply(extract_seed_value)

