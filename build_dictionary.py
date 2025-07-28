from collections import OrderedDict
import re

# USE THIS: https://fiatlingua.org/2014/09/
# AND THIS: https://chridd.nfshost.com/diachronica/index-diachronica.pdf
SPACE_BETWEEN_ENTRIES = '15pt'
FONT_SIZE = '20pt'

consonants = 'pbmfvθðtdnrszlɬʃʒkgŋhjwƛ'
vowels = 'aeiouə'

voiced_consonants = 'bdgmnlrvzʒŋ'
voiceless_consonants = 'ptfθsʃkhƛɬ'

stops = 'ptkbdg'
voiceless_stops = 'ptk'

sonorants = 'lmnŋrjw'
glides = 'jw'
liquids = 'lr'

fricatives = 'fvθðszʒʃhɬ'
affricates = 'ƛ'
approximates = 'ɹj'

stress_mark = "ˈ"

plural_marker = 'e'

def mark_stress(word):
    # Define the pattern to capture syllables
    pattern = fr'([{consonants}]*[{vowels}][{consonants}]*)'
    
    # Find all syllables in the word
    syllables = re.findall(pattern, word)
    if len(syllables) == 0:
        print(f'No syllables found in {word}')
        return word
    # Determine which syllable to stress
    if len(syllables) > 1:
        # Find the stressed syllable (penultimate)
        stressed_syllable = syllables[-2]
        # Find the position of the vowel in the stressed syllable
        match = re.search(fr'[{vowels}]', stressed_syllable)
        if match:
            # Insert the stress mark before the vowel
            stressed_syllable = stressed_syllable[:match.start()] + stress_mark + stressed_syllable[match.start():]
        # Replace the syllable with the stressed version
        syllables[-2] = stressed_syllable
    else:
        # Find the position of the vowel in the only syllable
        match = re.search(fr'[{vowels}]', syllables[0])
        if match:
            # Insert the stress mark before the vowel
            syllables[0] = syllables[0][:match.start()] + stress_mark + syllables[0][match.start():]
    
    # Reconstruct the word with stress marks
    stressed_word = ''.join(syllables)
    
    return stressed_word

def unmark_stress(word):
    return word.replace(stress_mark, "")

def vowel_loss_between_voiceless_consonants_unless_stressed(word):
    pattern = f"([{voiceless_consonants}])([{vowels}])([{voiceless_consonants}])"
    stressed = mark_stress(word)
    
    def replacement(match):
        # will only match unstressed vowels, since stressed vowels are marked with an apostrophe
        preceding, _, following = match.groups()
        return preceding + following  # Apply the transformation if unstressed
    
    return unmark_stress(re.sub(pattern, replacement, stressed))


def voiceless_stop_to_voiced_between_voiced(word):
    voiced_sounds = f'{vowels}{voiced_consonants}'
    voiceless_stops = {
        'p': 'b',
        't': 'd',
        'k': 'g'
    }
    for voiceless, voiced in voiceless_stops.items():
        pattern = f"([{voiced_sounds}]){voiceless}([{voiced_sounds}])"
        word = re.sub(pattern, r'\1' + voiced + r'\2', word)
    return word

def no_voiceless_stops_in_clusters(word):
    pattern = f"([{consonants}]+[{voiceless_stops}])"

    def replacement(match):
        # Extract the matched cluster
        cluster = match.group(0)
        # Find the first voiceless stop in the cluster and return the cluster without the last voiceless stop
        return cluster[:-1]  # Remove the last character which is a voiceless stop

    return re.sub(pattern, replacement, word)


def change_bardotlessj(word):
    return word.replace('ɟ', 'j')

def no_stops_after_fricatives(word):
    for fric in fricatives:
        for stop in stops:
            pattern = fric + stop
            word = word.replace(pattern, fric)
    return word

def no_stops_after_liquids(word):
    for liquid in liquids:
        for stop in stops:
            pattern = liquid + stop
            word = word.replace(pattern, liquid)
    return word

def no_stops_after_glides(word):
    for glide in glides:
        for stop in stops:
            pattern = glide + stop
            word = word.replace(pattern, glide)
    return word

def velar_hardening(word):
    # word_finally or before voiceless consonants
    pattern = fr'k(?=[{voiceless_consonants}]|$)'
    return re.sub(pattern, 'k', word)

def no_fricative_clusters(word):
    pattern = f"[{fricatives}][{fricatives}]"
    return re.sub(pattern, lambda x: x.group()[0], word)

def loss_of_h(word):
    # Remove 'h' between vowels or at the end of the word
    word = re.sub(fr'(?<=[{vowels}])h([{vowels}])', r'\1', word)
    word = re.sub(r'h$', '', word)
    return word

def vowel_combinations(word):
    word = re.sub(fr'ai(?=[^{vowels}]|$)', 'i', word)
    word = re.sub(r'aa', 'a', word)
    word = re.sub(r'ei', 'e', word)
    return word

def no_double_consonants(word):
    for consonant in consonants:
        pattern = f"{consonant}{consonant}"
        word = word.replace(pattern, consonant)
    return word

def no_repeated_vowels(word):
    for vowel in vowels:
        pattern = f"{vowel}{vowel}"
        word = word.replace(pattern, vowel)
    return word

def approximate_loss_after_o_or_u(word):
    pattern = fr'([ou])([{approximates}])'
    return re.sub(pattern, r'\1', word)

def vowel_loss_before_approximate(word):
    pattern = fr'([{vowels}])([{approximates}])'
    return re.sub(pattern, r'\2', word)

def nasal_assimilation(word):
    # Define the replacements
    replacements = {
        r'md': 'nd',
        r'np': 'mp',
        r'nk': 'ŋg',
        r'ng': 'ŋg',  # Additional replacements
        r'nt': 'nd',
        r'nc': 'ŋg',
        r'nj': 'ndʒ',
        r'ŋk': 'ŋg',
    }
    
    # Apply each replacement using regular expressions
    for pat, repl in replacements.items():
        word = re.sub(pat, repl, word)
    
    return word


def word_initial_vowel_loss_unless_stressed(word):
    stressed = mark_stress(word)
    # Do not apply if the vowel is stressed (has an apostrophe after it)
    if re.match(fr'^{stress_mark}[{vowels}]', stressed):
        return word
    # Apply the rule otherwise
    return re.sub(fr'^([{vowels}])', '', word)

def f_to_phi_at_word_end(word):
    return re.sub(r'f$', 'ɸ', word)

def word_final_vowel_loss_unless_stressed(word):
    stressed = mark_stress(word)
    # Do not apply if the vowel is stressed (has an apostrophe before it)
    if re.search(fr'{stress_mark}[{vowels}]$', stressed):
        return word
    # Apply the rule otherwise
    pattern = fr'([{vowels}])$'
    return re.sub(pattern, '', word)

def theta_r(word):
    # Get the stressed version of the word
    stressed = mark_stress(word)

    # Find all occurrences of "θir"
    matches = list(re.finditer(r'θir', word))
    
    # Create a new word to store the transformation result
    new_word = list(word)
    
    # Iterate through each match and transform if unstressed
    offset = 0
    for match in matches:
        start, end = match.span()
        if not re.search(rf"θ{stress_mark}i", stressed[start:end]):
            # Apply the transformation
            new_word[start + offset:end + offset] = 'θr'
            offset += -1  # Adjust offset due to length change (3 characters "θir" -> 2 characters "θr")
    
    return ''.join(new_word)


def no_stops_after_nasals(word):
    # Define the replacements
    replacements = {
        r'ŋk': 'ŋ',
        r'mp': 'm',
        r'ŋg': 'ŋ'
    }
    
    # Apply each replacement using regular expressions
    for pat, repl in replacements.items():
        word = re.sub(pat, repl, word)
    
    return word


def no_stops_after_sonorants(word):
    for sonorant in sonorants:
        for stop in stops:
            pattern = sonorant + stop
            word = word.replace(pattern, sonorant)
    return word


def ae_to_a(word):
    return word.replace('ae', 'a')

def no_coda_stops(word):
    stops = 'pb'
    for stop in stops:
        word = re.sub(f'{stop}(?=[^aeiou]|$)', 'm', word)
    return word

def no_final_e(word):
    pattern = fr'([e])$'
    return re.sub(pattern, '', word)

def y_to_sh(word):
    return word.replace('ʒ', 'ʃ')

def z_to_s(word):
    return word.replace('z', 's')

def unvoice_th(word):
    return word.replace('ð', 'θ')

def rhotacism_between_glides(word):
    pattern = f'([{glides}])r([{glides}])'
    return re.sub(pattern, r'\1r\2', word)

def rhotacism_between_vowels(word):
    pattern = f'([{vowels}])r([{vowels}])'
    return re.sub(pattern, r'\1r\2', word)

def no_fricatives_after_affricates(word):
    # Define the pattern to match affricates followed by fricatives
    pattern = f'([{affricates}])([{fricatives}])'
    # Replace the matched pattern with just the affricate
    return re.sub(pattern, r'\1', word)

def no_affricates_after_fricatives(word):
    # Define the pattern to match fricatives followed by affricates
    pattern = f'([{fricatives}])([{affricates}])'
    # Replace the matched pattern with just the fricative
    return re.sub(pattern, r'\1', word)


#Stop Cluster Simplification
def stop_cluster_simplification(word):
    # /pt/, /kt/, /pk/ → /p/, /k/, /p/
    pattern = r'pt|kt|pk'
    return re.sub(pattern, lambda m: m.group()[0], word)

# Fricative Clusters Harden with Epenthetic Stops
def fricative_cluster_hardening(word):
    # /sʃ/ → /tsʃ/, /ɬʃ/ → /tɬʃ/
    pattern = r'sʃ|ɬʃ'
    return re.sub(pattern, lambda m: 't' + m.group(), word)

#  Nasal Deletion Before Voiceless Obstruents
def nasal_deletion_before_voiceless_obstruents(word):
    #/n/ → ∅ / __[p t k f θ ʃ]
    pattern = fr'n(?=[{voiceless_consonants}])'
    return re.sub(pattern, '', word)

# Reduplicant Vowel Reduction
# Rule: CV-CV → Cə-CV
def reduplicant_vowel_reduction(word):
    stressed_word = mark_stress(word)
    # except when stressed
    stressed_pattern = fr'^([{consonants}]){stress_mark}([{vowels}])\1([{vowels}])'
    if re.match(stressed_pattern, stressed_word):
        return word
    pattern = fr'^([{consonants}])([{vowels}])\1([{vowels}])'
    return re.sub(pattern, r'\1ə\1\3', word)



# List of sound changes
sound_changes = [
    {'rule': 1000, 'description': 'Vowel loss between voiceless consonants in unstressed syllables', 'function': vowel_loss_between_voiceless_consonants_unless_stressed},
    {'rule': 2000, 'description': 'Voiceless stop between voiced sounds become voiced', 'function': voiceless_stop_to_voiced_between_voiced},
    {'rule': 2100, 'description': 'Vowel loss before affricate', 'function': vowel_loss_before_approximate},
    {'rule': 2200, 'description': 'Velar hardening k > k', 'function': velar_hardening},
    {'rule': 2300, 'description': 'ə lost', 'function': lambda x: x.replace('ə', '')},
    {'rule': 3000, 'description': 'No voiceless stops in clusters', 'function': no_voiceless_stops_in_clusters},
    {'rule': 3500, 'description': 'ɟ to j', 'function': change_bardotlessj},
    {'rule': 3500, 'description': 'Rhotacism GsG > GrG and GʒG > GrG', 'function': rhotacism_between_glides},
    {'rule': 3501, 'description': 'Rhotacism VsV > VrV to VʒV > VrV', 'function': rhotacism_between_vowels},
    {'rule': 4500, 'description': 'No stops after fricatives', 'function': no_stops_after_fricatives},
    {'rule': 4501, 'description': 'No stops after liquids', 'function': no_stops_after_liquids},
    {'rule': 4502, 'description': 'No fricative clusters', 'function': no_fricative_clusters},
    {'rule': 4503, 'description': 'No stops after glides', 'function': no_stops_after_glides},
    {'rule': 5000, 'description': 'h is lost between vowels and at the end of words', 'function': loss_of_h},
    {'rule': 5500, 'description': 'Vowel combinations', 'function': vowel_combinations},
    {'rule': 6000, 'description': 'Nasal assimilation', 'function': nasal_assimilation},
    {'rule': 6200, 'description': 'Approximate loss after o or u', 'function': approximate_loss_after_o_or_u},
    {'rule': 6300, 'description': 'Vowel loss before approximates', 'function': vowel_loss_before_approximate},
    {'rule': 6400, 'description': 'Nasal deletion before voiceless obstruents', 'function': nasal_deletion_before_voiceless_obstruents}, 
    {'rule': 6500, 'description': 'No double consonants', 'function': no_double_consonants},
    {'rule': 7500, 'description': 'Word-initial vowel loss', 'function': word_initial_vowel_loss_unless_stressed},
    {'rule': 7501, 'description': 'f to ɸ at the end of words', 'function': f_to_phi_at_word_end},
    {'rule': 8000, 'description': 'θr unless stressed', 'function': theta_r},
    {'rule': 8500, 'description': 'No stops after nasals', 'function': no_stops_after_nasals},
    {'rule': 8750, 'description': 'No stops after any sonorant', 'function': no_stops_after_sonorants},
    {'rule': 9200, 'description': 'Reduplicant vowel reduction', 'function': reduplicant_vowel_reduction}, # big change
    {'rule': 9500, 'description': 'Word-final vowel loss', 'function': word_final_vowel_loss_unless_stressed},
    {'rule': 10000, 'description': 'ae to a', 'function': ae_to_a},
    {'rule': 11000, 'description': 'No coda stops', 'function': no_coda_stops},
    {'rule': 11500, 'description': 'Stop cluster simplification', 'function': stop_cluster_simplification},
    {'rule': 11990, 'description': 'ə lost', 'function': lambda x: x.replace('ə', '')},
    {'rule': 12000, 'description': 'z to s', 'function': z_to_s},
    {'rule': 12001, 'description': 'ʒ to ʃ', 'function': y_to_sh},
    {'rule': 12002, 'description': 'ð to θ', 'function': unvoice_th},
    {'rule': 12003, 'description': 'No repeated vowels', 'function': no_repeated_vowels},
    {'rule': 12004, 'description': 'No word-final e', 'function': no_final_e},
    {'rule': 12005, 'description': 'No repeated consonants', 'function': no_double_consonants},
    {'rule': 13000, 'description': 'No fricative clusters', 'function': no_fricative_clusters},
    {'rule': 14000, 'description': 'No fricatives after affricates', 'function': no_fricatives_after_affricates},
    {'rule': 14001, 'description': 'No affricates after fricatives', 'function': no_affricates_after_fricatives},
]

# Function to apply all sound changes
def apply_sound_changes(year_and_word, max_year=None):
    print(year_and_word)
    year, word, _, _, pos, _ = year_and_word
    history = [(year, word)]
    if year == -1:
        # skip sound changes for permanent words (proper nouns and markers)
        return word, [(0, word)]
    for change in sound_changes:
        if change['rule'] < year:
            continue
        if max_year is not None and change['rule'] > max_year:
            break
        
        word = change['function'](word)
        if unmark_stress(word) != history[-1][1]:
            history.append((change['rule'], word))
    word = history[-1][1]

    if pos == 'Ns' or pos == 'Ps':
        # add plural marker
        if not word.endswith(plural_marker):
            word += plural_marker

    return word, history

# Function to format the final word for LaTeX
def format_for_latex(word):
    word_chars = list(word)
    replacements = {
        'ʃ': r'{\textesh}',
        'ŋ': r'{\ng}',
        'θ': r'{\texttheta}',
        'ð': r'{\dh}',
        'ɟ': r'{\textbardotlessj}',
        'ɬ': r'{\textbeltl}',
        'ʒ': r'{\textyogh}',
        'ƛ': r'{\texttoptiebar{t\textbeltl}}',
        'ə': r'{\textschwa}',
        'ˈ': r'{\textprimstress}',
        'j': r'y',
        'ɸ': r'{\textphi}',
        't': r'{\textsubbridge{t}}',
        # Add more replacements as necessary
    }

    for ipa_char, latex_char in replacements.items():
        for i, char in enumerate(word_chars):
            if char == ipa_char:
                word_chars[i] = latex_char
    return ''.join(word_chars)

def borrowed_sound_changes(borrowed):
    always_replaced = {
        'ɹ':'r',
        'β':'b',
    }
    borrowed_replaced = []
    for b in borrowed:
        word = b[1]
        for s,r in always_replaced.items():
            word = word.replace(s,r)
            print(b[1], word,s,r)
        borrowed_replaced.append((b[0],word,b[2],b[3],b[4],b[-1]))
    return borrowed_replaced

def romanization(word):
    replacements = {
        'ʃ': r'sh',
        'ŋ': r'ng',
        'θ': r'th',
        'ð': r'dh',
        'ɟ': r'j',
        'ɬ': r'lh',
        'ʒ': r'z',
        'j': r'y',
        'ƛ': r'tl',
        'ə': r'e',
        'ɸ': r'f',
    }
    for roman_char, latex_char in replacements.items():
        word = word.replace(roman_char, latex_char)
    return word

def get_dictionary_csv(word_after_changes, translation, stress, rom, pos, notes, roots):
    csv_lines = []
    csv_lines.append(f"{translation.strip()},{rom},/{stress}/,{pos},{roots}")
    return "\n".join(csv_lines)

def get_dictionary_latex(history, translation,roots,pos,notes):
    # Start tabular environment with dynamic number of columns

    raw_word = history[-1][1]

    max_rows = 1000
    # if len(raw_word) > 8:
        # max_rows = 4

    text = ''
    text += fr'\vspace{{{SPACE_BETWEEN_ENTRIES}}}' + '\n'
    text+= r'\begin{nopagebreak}' + '\n'
    text+=rf'\noindent{{\fontsize{{{FONT_SIZE}}}{{10pt}}\textbf{{{romanization(raw_word)}}} }} \textit{{{translation}}}' 
    text+= f' ({pos})'
    text+= r'\\' + '\n'
    text+=rf'\noindent {{\tovian \fontsize{{{FONT_SIZE}}}{{10pt}} \textbf{{{romanization(raw_word)}}} }}'
    text+= r'\\' + '\n'
    text+=rf'\noindent /{format_for_latex(mark_stress(raw_word))}/'
    text+= r'\\' + '\n'
    if roots!='_':
        text+=rf'\noindent lit. {roots}'
        text+= r'\\' + '\n'
    if notes!='_':
        text+=rf'\noindent \textit{{{notes}}}'
        text+= r'\\' + '\n'
    text +='\n\n'
    text += r'\noindent History:' + '\n'

    # split up into groups of 5 max
    groups = [history[i:i+max_rows] for i in range(0, len(history), max_rows)]
    for idx, group in enumerate(groups):
        num_columns = 3
        # num_columns = max(2, num_columns)
        column_format = ''+'c' * num_columns
        # if idx >0:
        text+='\n'+ r'\vspace{-0pt}' + '\n' + r'\hspace{40pt}'+ '\n'
        text += rf'\begin{{tabular}}{{{column_format}}}' + '\n'
        
        this_group = group

        for j, (rule, word) in enumerate(this_group):
            text += fr'\textit{{{rule}}} & '
            text += fr'/{format_for_latex(word)}/' 
            if (j!=len(this_group)-1) or (idx != len(groups)-1):
                text += r'&$\rightarrow$ & '
            else:
                text += r'& '
        
        text+=r'\\'
    
        text += '\n'+r'\end{tabular}' + '\n\n'
    text+=r'\vspace{20pt}\hline' + '\n\n'
    text += r'\end{nopagebreak}' + '\n'
    text+=r'\filbreak' + '\n\n'
    return text


def load_roots():
    words = []
    with open('roots.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader) # Skip the header
        for row in reader:
            if len(row) == 0: continue
            words.append((int(row[0]), row[1], row[2],row[3],row[4],row[5]))
    return words


def load_borrowed():
    words = []
    with open('borrowed.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader) # Skip the header
        for row in reader:
            if len(row) == 0: continue
            words.append((int(row[0]), row[1], row[2],row[3],row[4], row[6]))
    words = borrowed_sound_changes(words)
    return words


def remove_obsolete_marker(word):
    return word.replace(" (obsolete)", "")


def find_root_or_compound(word, roots, compounds):
    for root in roots:
        r = remove_obsolete_marker(root[2]).strip()
        if r == word:
            return root
        if word in r.split('/'):
            # also find polysemous roots
            return root
    for compound in compounds:
        c = remove_obsolete_marker(compound[2]).strip()
        if c == word:
            return compound
        if word in c.split('/'):
            # also find polysemous compounds
            return compound
    print(f"Could not find {word}")
    return None

def form_compounds(roots):
    compounds = []
    with open('compounds.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader) # Skip the header
        for row in reader:
            if len(row) == 0: continue
            compound_roots = row[2]
            compound_roots = compound_roots.split('+')
            for R in compound_roots:
                root = find_root_or_compound(R, roots, compounds)
                if root is None:
                    raise ValueError(f"Root {R} not found")
                # apply sound changes up to the year of the compound to each root
                root = apply_sound_changes(root, int(row[0]))[0]
                compound_roots[compound_roots.index(R)] = root
            compound = "".join(compound_roots)
            compounds.append((int(row[0]), compound, row[1], row[2], row[3], row[4]))
    return compounds

import argparse
import csv
# Main function
def main():
    parser = argparse.ArgumentParser(description='Build a dictionary from roots, compounds, and borrowed words.')
    parser.add_argument('--interactive','-i', action='store_true', help='Run in interactive mode')
    parser.add_argument('--max_year', '-y', type=int, help='Maximum year for sound changes')
    args = parser.parse_args()

    roots = load_roots()
    compounds = form_compounds(roots)
    borrowed = load_borrowed() 

    input_words = roots + compounds + borrowed 
    interactive_dict = {}
    latex_histories = {}
    csv_histories = []
    for input_word in input_words:
        year = input_word[0]
        translation = input_word[2]
        roots = input_word[3]
        pos = input_word[4]
        notes = input_word[-1]
        word_after_changes, history = apply_sound_changes(input_word, max_year=args.max_year)
        
        final_word = format_for_latex(word_after_changes)
        if not args.interactive:
            for rule, word in history:
                print(f'{rule}: {mark_stress(word)}')
        
        rom = romanization(word_after_changes)
        stress = mark_stress(word_after_changes)
        csv_history = get_dictionary_csv(word_after_changes, translation, stress, rom, pos, notes, roots)
        csv_histories.append(csv_history)
        

        for definition in translation.split('/'):
            interactive_dict[definition.strip()] = (final_word, pos, history, rom, stress, notes)
        
        if not args.interactive:
            print(stress)
            print(rom)
            print()

        latex_history = get_dictionary_latex(history, translation, roots, pos, notes)
        latex_histories[translation] = latex_history

    # sort latex_histories by key
    latex_histories = OrderedDict(sorted(latex_histories.items(), key=lambda x: x[0].lower()))
    
    # split csv histories into duplicate entries if multiple definitions with /
    expanded_csv_histories = []
    for csv_history in csv_histories:
       # add identical column as _
        words = csv_history.strip().split(',')[0].split('/')
        if len(words) > 1:
            for w in words:
                parts = csv_history.strip().split(',')
                new_csv = f'{w.strip()},' + ','.join(parts[1:])
                # add to identical column
                new_csv = new_csv.rsplit(',',0)[0] +","+ "/".join(words)
                expanded_csv_histories.append(new_csv)
        else:
            expanded_csv_histories.append(csv_history.strip()+',_')
    # sort csv_histories by the first line's final word, numbers at end of list, pos=CASE at end of list 
    def sort_dict(x):
        first_line = x.splitlines()[0]
        first_word = first_line.split('","')[0].strip('"').lower()
        pos = first_line.split(',')[3].strip('"')
        # if pos is 'case' or 'ps' or 'ns', put at end
        if pos in ['CASE', 'CLASS', 'PLURAL']:
            return 'zzz' + first_word
        if not first_word[0].isdigit():
            return first_word
        else:
            return 'zzzz' + first_word
    expanded_csv_histories = sorted(expanded_csv_histories, key=sort_dict)
    
    filename = 'dictionary.tex'
    if args.max_year is not None:
        filename = f'dictionary_{args.max_year}.tex'
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(r'\twocolumn' + '\n')
        for translation, latex_history in latex_histories.items():
            file.write(latex_history + '\n\n')
        file.write(r'\onecolumn' + '\n')
    
    csv_filename = 'dictionary.csv'
    if args.max_year is not None:
        csv_filename = f'dictionary_{args.max_year}.csv'
    #also save to pages/
    pages_filename='pages/'+csv_filename
    for fname in [csv_filename, pages_filename]:
        with open(fname, 'w', encoding='utf-8') as file:
            file.write('English,Tovian,IPA,POS,Roots,Identical\n')
            for csv_history in expanded_csv_histories:
                file.write(csv_history + '\n\n')
            
        
    if args.interactive:
        print("Interactive mode enabled. Type 'q' to quit.")
        while True:
            user_input = input("Enter a word or definition: ").strip()
            if user_input.lower() == 'q':
                break
            if user_input in interactive_dict:
                final_word, pos, history, rom, stress, note = interactive_dict[user_input]
                print(f"Final Word: {final_word}, POS: {pos}, Romanization: {rom}, Stress: {stress}")
                if note!="_" and note:
                    print(f"Note: {note}")
                for rule, word in history:
                    print(f'{rule}: {mark_stress(word)}')
            else:
                print("Word not found in the dictionary. 'q' to quit.")

if __name__ == "__main__":
    main()
