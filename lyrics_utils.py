import logging
import re

class LyricsUtils:
    @staticmethod
    def is_lyric_page(lyric_string):
        # Check several conditions which indicate an invalid lyrics page
        if not lyric_string or len(lyric_string) < 40:
            return False

        conditions = [
            "We are not in a position to display these lyrics due to licensing restrictions.",
            "Select your carrier...",
            "Unfortunately, we aren't authorized to display these lyrics",
            "No lyrics text found for this track.",
            "No lyrics found for this song",
            "Lamentablemente no estamos autorizados",
            "Unfortunately we're not authorized",
            "Ã³"
        ]

        for condition in conditions:
            if condition in lyric_string:
                return False

        return True

    @staticmethod
    def get_clean_title(name):
        # Verwijder bestandsextensie
        filename = re.sub(r"^(.+)\.\w+$", r"\1", name)

        # Zoek naar het haakje "(" en verwijder tekst daarna
        parpos = filename.find("(")
        if parpos != -1:
            filename = filename[:parpos].strip()

        if "|" in filename and "-" not in filename:
            filename = filename.replace("|", "-")  # Vervang "|" door "-" als er geen "-" is

        if "–" in filename and "-" not in filename:
            filename = filename.replace("–", "-")  # Vervang "–" door "-" als er geen "-" is

        verticalpos = filename.find("|")
        if verticalpos != -1:
            filename = filename[:verticalpos].strip()

        squarepos = filename.find("[")
        if squarepos != -1:
            filename = filename[:squarepos].strip()

        # Zoek het LAATSTE koppelteken (hoofd separator tussen artiest en titel)
        pos = filename.rfind("-")

        if pos == -1 or pos == len(filename) - 1:  # Geen "-" of "-" is laatste teken
            return name  # Ongeldige invoer

        # Controleer of er een spatie NA het koppelteken komt (anders hoort "-" bij de artiest)
        if filename[pos + 1] != " ":
            return name  # Ongeldige invoer (bijv. "AC/DC")

        # Splits bij de LAATSTE "-" en neem de titel
        artist, title = filename[:pos].strip(), filename[pos + 1:].strip()

        if not title:
            return ""  # Ongeldige invoer

        # Verwijder specifieke woorden zoals "ft.", "feat.", en "- Lyrics"
        title = re.sub(r"ft\..*", "", title, flags=re.IGNORECASE)  # Verwijder "ft."
        title = re.sub(r"feat\..*", "", title, flags=re.IGNORECASE)  # Verwijder "feat."
        title = re.sub(r"\s-\sLyrics", "", title, flags=re.IGNORECASE)  # Verwijder " - Lyrics"
        title = re.sub(r"\sft\s.*", "", title, flags=re.IGNORECASE)  # Remove " ft " and everything that follows

        # Geef de opgeschoonde titel terug
        return title

    @staticmethod
    def get_clean_artist(name):
        # Verwijder de extensie
        filename = re.sub(r"^(.+)\.\w+$", r"\1", name)

        # Verwijder termen als "ft." en "feat."
        filename = re.sub(r"ft\..*", "", filename)  # Verwijder "ft."
        filename = re.sub(r"feat\..*", "", filename)  # Verwijder "feat."
        filename = re.sub(r"\s-\sLyrics", "", filename, flags=re.IGNORECASE)  # Verwijder " - Lyrics"
        filename = re.sub(r"\sOficial", "", filename, flags=re.IGNORECASE)  # Verwijder " Oficial"
        filename = re.sub(r"\sft\s.*", "", filename, flags=re.IGNORECASE)  # Remove " ft " and everything that follows

        # Zoek naar het haakje "(" en verwijder tekst daarna
        parpos = filename.find("(")
        if parpos != -1:
            filename = filename[:parpos].strip()

        if "|" in filename and "-" not in filename:
            filename = filename.replace("|", "-")  # Vervang "|" door "-" als er geen "-" is

        if "–" in filename and "-" not in filename:
            filename = filename.replace("–", "-")  # Vervang "–" door "-" als er geen "-" is

        verticalpos = filename.find("|")
        if verticalpos != -1:
            filename = filename[:verticalpos].strip()

        squarepos = filename.find("[")
        if squarepos != -1:
            filename = filename[:squarepos].strip()

        # Zoek het eerste koppelteken
        hyphenpos = filename.find("-")
        if hyphenpos == -1:
            return ""  # Ongeldige invoer

        # Bepaal hoeveel terug te gaan, standaard 1
        space_after_pos = filename.find(" ", hyphenpos)
        if space_after_pos == -1 or space_after_pos > hyphenpos + 1:
            amount = 1
        else:
            amount = 2

        # Controleer op tweede koppelteken
        hyphenpostwo = filename.find("-", hyphenpos + 1)
        if hyphenpostwo == -1 or hyphenpostwo > len(filename) - 4:
            # Hier aftrekken van `amount` is niet zinvol - hou gewoon rekening met het eerste koppelteken
            return filename[:hyphenpos].strip()
        else:
            return filename[:hyphenpostwo - amount].strip()

    @staticmethod
    def levenshtein_distance(str1, str2):
        # Create a matrix to store distances
        len_str1 = len(str1)
        len_str2 = len(str2)

        # Initialize a (len_str1+1) x (len_str2+1) matrix
        matrix = [[0] * (len_str2 + 1) for _ in range(len_str1 + 1)]

        # Fill the first row and first column
        for i in range(len_str1 + 1):
            matrix[i][0] = i
        for j in range(len_str2 + 1):
            matrix[0][j] = j

        # Compute the distance
        for i in range(1, len_str1 + 1):
            for j in range(1, len_str2 + 1):
                cost = 0 if str1[i - 1] == str2[j - 1] else 1
                matrix[i][j] = min(matrix[i - 1][j] + 1,  # Deletion
                                   matrix[i][j - 1] + 1,  # Insertion
                                   matrix[i - 1][j - 1] + cost)  # Substitution

        return matrix[len_str1][len_str2]

    @staticmethod
    def similarity_percentage(source, str1, str2):
        # Calculate Levenshtein distance
        distance = LyricsUtils.levenshtein_distance(str1.lower(), str2.lower())
        max_len = max(len(str1), len(str2))

        # Calculate similarity as a percentage
        similarity = (1 - distance / max_len) * 100

        if similarity < 80:
            logging.info(f"{source}: {str1} is only {similarity}% similar to {str2}.")

        return similarity
