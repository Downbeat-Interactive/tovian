from collections import OrderedDict
import re

# USE THIS: https://fiatlingua.org/2014/09/
# AND THIS: https://chridd.nfshost.com/diachronica/index-diachronica.pdf
SPACE_BETWEEN_ENTRIES = '15pt'
FONT_SIZE = '20pt'

consonants = 'pbmfvθðtdnrszlɬʃʒkgŋhħjwƛ'
vowels = 'aeiouə'

voiced_consonants = 'bdgmnlrvzʒŋ'
voiceless_consonants = 'ptfθsʃkhħƛɬ'

stops = 'ptkbdg'
voiceless_stops = 'ptk'

sonorants = 'lmnŋrjw'
glides = 'jw'
liquids = 'lr'
nasals = 'mnŋ'

fricatives = 'fvθðszʒʃhħɬ'
affricates = 'ƛ'
approximates = 'ɹj'

stress_mark = "ˈ"

plural_marker = 'e'

light_morphemes = ['fe', 'la', 're', 'li']

def find_syllables(word):
    pattern = fr'([{consonants}]*[{vowels}][{consonants}]*)'
    syllables = re.findall(pattern, word)
    return syllables

def count_syllables(word):
    syllables = find_syllables(word)
    return len(syllables)

def mark_syllable_boundaries(word):
    syllables = find_syllables(word)
    if len(syllables) == 0:
        return word
    # Reconstruct the word with '.' between syllables
    marked_word = '.'.join(syllables)
    return marked_word

def mark_stress(word):
    # Define the pattern to capture syllables
    # Find all syllables in the word
    syllables = find_syllables(word)
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

def dotted_with_stress(word):
    """Return a display-only IPA with syllable dots and stress mark.
    Expects an undecorated word (no stress marks)."""
    syllables = find_syllables(word)
    if len(syllables) == 0:
        return word
    idx = 0 if len(syllables) == 1 else len(syllables) - 2
    # insert stress before the first vowel in the target syllable
    m = re.search(fr'[{vowels}]', syllables[idx])
    if m:
        s = syllables[idx]
        syllables[idx] = s[:m.start()] + stress_mark + s[m.start():]
    return '.'.join(syllables)

def vowel_loss_between_voiceless_consonants_unless_stressed(word):
    pattern = f"([{voiceless_consonants}])([{vowels}])([{voiceless_consonants}])"
    stressed = mark_stress(word)
    
    def replacement(match):
        # will only match unstressed vowels, since stressed vowels are marked with an apostrophe
        preceding, _, following = match.groups()
        return preceding + following  # Apply the transformation if unstressed
    
    return unmark_stress(re.sub(pattern, replacement, stressed))


def h_to_ħ(word):
    return word.replace('h', 'ħ')

def b_to_d(word):
    return word.replace('b', 'd')

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
        r'ng': 'ŋg', 
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



#θ → s / _k
def theta_s_before_k(word):
    pattern = r'θ(?=k)'
    return re.sub(pattern, 's', word)

#θ → t / {p,t,k}_
def theta_t_after_voiceless_stops(word):
    pattern = fr'(?<=[{voiceless_stops}])θ'
    return re.sub(pattern, 't', word)

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
    pattern = fr'([{nasals}])([{stops}])'
    return re.sub(pattern, r'\1', word)

def no_stops_after_nasals_except_when_split_syllable(word):
    syl = mark_syllable_boundaries(word)
    parts = syl.split('.')
    new_parts = []
    for part in parts:
        for nasal in nasals:
            for stop in stops:
                pattern = nasal + stop
                if pattern in part:
                    # only remove if not split syllable
                    if len(part) > 2 and part.index(pattern) != 0 and part.index(pattern) != len(part)-2:
                        part = part.replace(pattern, nasal)
        new_parts.append(part)
    return ''.join(new_parts)

def no_stops_after_sonorants(word):
    for sonorant in sonorants:
        for stop in stops:
            pattern = sonorant + stop
            word = word.replace(pattern, sonorant)
    return word


def ae_to_a(word):
    return word.replace('ae', 'a')

def p_b_to_m(word): # TODO
    stops = 'pb'
    for stop in stops:
        word = re.sub(f'{stop}(?=[^{vowels}]|$)', 'm', word)
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

#s → ∅ / V_V 
def loss_of_s_between_vowels(word):
    pattern = fr'(?<=[{vowels}])s(?=[{vowels}])'
    return re.sub(pattern, '', word)

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

# /ʃd/ → [ɬt]
def shd_to_lht(word):
    pattern = r'ʃd'
    return re.sub(pattern, 'ɬt', word)

#  Nasal Deletion Before Voiceless Obstruents
def nasal_deletion_before_voiceless_obstruents(word):
    #/n/ → ∅ / __[p t k f θ ʃ]
    pattern = fr'n(?=[{voiceless_consonants}])'
    return re.sub(pattern, '', word)


def schwa_deletion(word):
    return word.replace('ə', '')


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


# /npk/ → /nk/ or /pk/ (depends on syllabification)
def npk_to_nk_or_pk(word):
    syllables = find_syllables(word)
    if len(syllables) < 2:
        return word
    # Check if the first syllable ends with 'n' and the second starts with 'p'


def simplify_hn_to_n(word):
    return re.sub(r'hn', 'n', word)

def simplify_final_clusters(word):
    # e.g., /-rks/ → /-ks/, /-ndr/ → /-r/
    pattern = fr'([{consonants}])([{consonants}])$'
    # thr is allowed
    if word.endswith('θr'):
        return word
    return re.sub(pattern, r'\1', word)


def medial_syncope_unless_stressed(word):
    stressed = mark_stress(word)
    syllables = find_syllables(word)
    if len(syllables) < 3:
        return word
    # Check if the middle syllable is stressed
    middle_index = len(syllables) // 2
    middle_syllable = syllables[middle_index]
    if stress_mark in middle_syllable:
        return word
    # Remove the vowel from the middle syllable
    pattern = fr'([{consonants}])([{vowels}])([{consonants}])'
    parts = stressed.split('.')
    new_parts = []
    for i, part in enumerate(parts):
        if i == middle_index:
            # Remove the vowel from this part
            part = re.sub(pattern, r'\1\3', part)
        new_parts.append(part)
    return ''.join(new_parts)

def light_morpheme_simplification(word):
    stressed = mark_stress(word)
    for morpheme in light_morphemes:
        # Only delete if surrounded by other content and not stressed
        pattern = f'([a-z]+){morpheme}([a-z]+)'
        new_word = re.sub(pattern, r'\1\2', stressed)
        if new_word != word:
            return unmark_stress(new_word)
    return unmark_stress(word)

def reduplication_simplification(word):
    if count_syllables(word) < 3:
        return word
    # Match repeated syllables: e.g., la-la → la
    return re.sub(r'(\b\w{1,2})\1', r'\1', word)


def onset_cluster_simplification(word):
    # Simplify illegal CCC onsets, e.g., stl → sl or remove first C
    return re.sub(fr'\b([{consonants}])([{consonants}])([{consonants}])', r'\2\3', word)


def medial_vowel_loss(word):
    # Removes a medial unstressed vowel between consonants
    stressed = mark_stress(word)
    return unmark_stress(re.sub(fr'([{consonants}])([{vowels}])([{consonants}])', r'\1\3', stressed))


def simplify_sonorant_clusters_excluding_initial_mr(word):
      # e.g. lr → r, ln → n
    # Simplify sonorant+sonorant (l/r/m/n) sequences where awkward
    # return re.sub(fr'([{sonorants}])([{sonorants}])', r'\2', word)
    # except when initial mr
    if word.startswith('mr'):
        rest = word[2:]
        simplified_rest = re.sub(fr'([{sonorants}])([{sonorants}])', r'\2', rest)
        return 'mr' + simplified_rest
    else:
        return re.sub(fr'([{sonorants}])([{sonorants}])', r'\2', word)


def simplify_fricative_nasal_clusters(word):
    for fric in fricatives:
        for nasal in nasals:
            pattern = fric + nasal
            word = word.replace(pattern, nasal)
    return word


def simplify_initial_tl_n_cluster(word):
    return re.sub(r'^ƛn', 'n', word)


def simplify_initial_mf_to_m(word):
    return re.sub(r'^mf', 'm', word)

def epenthesis_in_initial_ml(word):
    return re.sub(r'^ml', 'mel', word)

def epenthesis_in_initial_lm(word):
    return re.sub(r'^lm', 'lem', word)

def epenthesis_in_initial_fm(word):
    return re.sub(r'^fm', 'fem', word)

def simplify_fricative_liquid_clusters(word):
    for fric in fricatives:
        for liquid in liquids:
            cluster = fric + liquid
            if cluster == 'θr':
                continue  # θr is allowed
            if cluster in word:
                # Default simplification: delete the liquid
                word = word.replace(cluster, fric)
    return word


def epenthetic_vowel_in_initial_double_nasal(word):
    return re.sub(fr'^([{nasals}])([{nasals}])', r'\1u\2', word)


def simplify_final_stop_sonorant_clusters(word):
    return re.sub(fr'([{stops}])([{sonorants}])$', r'\2', word)

def simplify_g_tl(word):
    return re.sub(r'gƛ', 'ƛ', word) 

def simplify_tl_to_ƛ(word):
    return re.sub(r'tl', 'ƛ', word)

def simplify_lh_to_ɬ(word):
    return re.sub(r'lh', 'ɬ', word)

def wiw_to_win(word):
    return re.sub(r'wiw', 'win', word)  

def epenthesis_in_ƛd_cluster(word):
    return re.sub(r'ƛd', 'ƛod', word)

def epenthesis_in_initial_t_sh_cluster(word):
    return re.sub(r'^tʃ', 'teʃ', word)

def simplify_lθ_to_θ(word):
    return re.sub(r'lθ', 'θ', word)


def dissimilate_fricative_reduplication(word):
    # Avoid fricative-vowel-fricative-vowel-fricative patterns (e.g., iθiθ to iθit)
    replacements = {
        'θ': 't',
        'ʃ': 'd',
        'ɬ': 'l',
    }
    for k,v in replacements.items():
        pattern = fr'([{vowels}]){k}([{vowels}]){k}'
        word = re.sub(pattern, fr'\1{k}\2{v}', word)
    return word


def metathesize_lr(word):
    return re.sub(r'lr', 'rl', word)
def metathesize_jf(word):
    return re.sub(r'jf', 'fj', word)

def epenthesize_initial_nθ(word):
    return re.sub(r'^nθ', 'meθ', word)

def nasal_assimilation_mθ_to_nθ(word):
    return re.sub(r'mθ', 'nθ', word)


# List of sound changes
sound_changes = [
    {'rule': 1000, 'description': 'Vowel loss between voiceless consonants in unstressed syllables', 'function': vowel_loss_between_voiceless_consonants_unless_stressed},
    {'rule': 2000, 'description': 'Voiceless stop between voiced sounds become voiced', 'function': voiceless_stop_to_voiced_between_voiced},
    {'rule': 2100, 'description': 'Vowel loss before affricate', 'function': vowel_loss_before_approximate},
    {'rule': 2200, 'description': 'Velar hardening k > k', 'function': velar_hardening},
    {'rule': 2300, 'description': 'ə lost', 'function': schwa_deletion},
    {'rule': 3000, 'description': 'No voiceless stops in clusters', 'function': no_voiceless_stops_in_clusters},
    {'rule': 3200, 'description': 'Medial vowel loss', 'function': medial_vowel_loss}, # huge change
    {'rule': 3500, 'description': 'ɟ to j', 'function': change_bardotlessj},
    {'rule': 3501, 'description': 'Rhotacism GsG > GrG and GʒG > GrG', 'function': rhotacism_between_glides},
    {'rule': 3502, 'description': 'Rhotacism VsV > VrV to VʒV > VrV', 'function': rhotacism_between_vowels},
    {'rule': 3503, 'description': 'Nasal assimilation mth > nth', 'function': nasal_assimilation_mθ_to_nθ},
    {'rule': 3503, 'description': 'epenthesize_initial_nθ', 'function': epenthesize_initial_nθ},
    {'rule': 4500, 'description': 'No stops after fricatives', 'function': no_stops_after_fricatives},
    {'rule': 4501, 'description': 'No stops after liquids', 'function': no_stops_after_liquids},
    {'rule': 4502, 'description': 'No fricative clusters', 'function': no_fricative_clusters},
    {'rule': 4503, 'description': 'No stops after glides', 'function': no_stops_after_glides},
    {'rule': 5000, 'description': 'h is lost between vowels and at the end of words', 'function': loss_of_h},
    {'rule': 5100, 'description': 's is lost between vowels', 'function': loss_of_s_between_vowels},
    {'rule': 5500, 'description': 'Vowel combinations', 'function': vowel_combinations},
    {'rule': 6000, 'description': 'Nasal assimilation', 'function': nasal_assimilation},
    {'rule': 6200, 'description': 'Approximate loss after o or u', 'function': approximate_loss_after_o_or_u},
    {'rule': 6240, 'description': 'hn > n', 'function': simplify_hn_to_n},
    {'rule': 6300, 'description': 'Vowel loss before approximates', 'function': vowel_loss_before_approximate},
    {'rule': 6400, 'description': 'Nasal deletion before voiceless obstruents', 'function': nasal_deletion_before_voiceless_obstruents}, 
    {'rule': 6401, 'description': 'tl → ƛ', 'function': simplify_tl_to_ƛ},
    {'rule': 6402, 'description': 'lh → ɬ', 'function': simplify_lh_to_ɬ},
    {'rule': 6500, 'description': 'No double consonants', 'function': no_double_consonants},
    {'rule': 6501, 'description': 'Simplify initial ƛn cluster', 'function': simplify_initial_tl_n_cluster},
    {'rule': 6502, 'description': 'Epenthesis in initial fm', 'function': epenthesis_in_initial_fm},
    {'rule': 6503, 'description': 'Metathesize lr', 'function': metathesize_lr},
    {'rule': 7400, 'description': 'Epenthesis in initial lm', 'function': epenthesis_in_initial_lm},
    {'rule': 7500, 'description': 'Word-initial vowel loss', 'function': word_initial_vowel_loss_unless_stressed},
    {'rule': 7501, 'description': 'f to ɸ at the end of words', 'function': f_to_phi_at_word_end},
    {'rule': 7501, 'description': 'Onset cluster simplification', 'function': onset_cluster_simplification},
    {'rule': 7502, 'description': 'Epenthesis in initial ml', 'function': epenthesis_in_initial_ml},
    {'rule': 7503, 'description': 'Metathesize jf', 'function': metathesize_jf},
    {'rule': 7600, 'description': 'Simplify sonorant clusters', 'function': simplify_sonorant_clusters_excluding_initial_mr},
    {'rule': 8000, 'description': 'θr unless stressed', 'function': theta_r},
    {'rule': 8500, 'description': 'No stops after nasals', 'function': no_stops_after_nasals_except_when_split_syllable},
    {'rule': 8750, 'description': 'No stops after any sonorant', 'function': no_stops_after_sonorants},
    {'rule': 9200, 'description': 'Reduplicant vowel reduction', 'function': reduplicant_vowel_reduction}, # big change
    {'rule': 9300, 'description': 'Epenthesis in ƛd clusters', 'function': epenthesis_in_ƛd_cluster},
    {'rule': 9500, 'description': 'Word-final vowel loss', 'function': word_final_vowel_loss_unless_stressed},
    {'rule': 10000, 'description': 'ae to a', 'function': ae_to_a},
    {'rule': 10500, 'description': 'θ to s before k', 'function': theta_s_before_k},
    {'rule': 10700, 'description': 'θ to t after voiceless stops', 'function': theta_t_after_voiceless_stops},
    {'rule': 11000, 'description': 'No coda stops', 'function': p_b_to_m},
    {'rule': 11001, 'description': 'b to d', 'function': b_to_d},
    {'rule': 11500, 'description': 'Stop cluster simplification', 'function': stop_cluster_simplification},
    {'rule': 11501, 'description': 'Simplify gƛ', 'function': simplify_g_tl},
    {'rule': 11600, 'description': 'Medial syncope', 'function': medial_syncope_unless_stressed},
    {'rule': 11990, 'description': 'ə lost', 'function': schwa_deletion},
    {'rule': 11995, 'description': 'Simplify initial mf to m', 'function': simplify_initial_mf_to_m},
    {'rule': 11996, 'description': 'Epenthetic vowel in initial double nasal', 'function': epenthetic_vowel_in_initial_double_nasal},
    {'rule': 12000, 'description': 'z to s', 'function': z_to_s},
    {'rule': 12001, 'description': 'ʒ to ʃ', 'function': y_to_sh},
    {'rule': 12002, 'description': 'ð to θ', 'function': unvoice_th},
    {'rule': 12003, 'description': 'Light morpheme simplification', 'function': light_morpheme_simplification},
    {'rule': 12004, 'description': 'Reduplication simplification', 'function': reduplication_simplification},
    {'rule': 12005, 'description': 'No repeated vowels', 'function': no_repeated_vowels},
    {'rule': 12006, 'description': 'No word-final e', 'function': no_final_e},
    {'rule': 12007, 'description': 'No repeated consonants', 'function': no_double_consonants},
    {'rule': 12400, 'description': 'Epenthetic vowel in initial tʃ', 'function': epenthesis_in_initial_t_sh_cluster},
    {'rule': 12500, 'description': 'Simplify fricative-liquid clusters', 'function': simplify_fricative_liquid_clusters},
    {'rule': 12501, 'description': 'Dissimilate fricative reduplication', 'function': dissimilate_fricative_reduplication},
    {'rule': 12502, 'description': 'Simplify lθ → l', 'function': simplify_lθ_to_θ},
    {'rule': 13000, 'description': 'No fricative clusters', 'function': no_fricative_clusters},
    {'rule': 13001, 'description': 'Simplify final consonant clusters to single consonant', 'function': simplify_final_clusters},
    {'rule': 13002, 'description': 'Simplify fricative-nasal clusters', 'function': simplify_fricative_nasal_clusters},
    {'rule': 13003, 'description': 'wiw to win', 'function': wiw_to_win},
    {'rule': 13004, 'description': 'Simplify stop sonorany clusters word finally', 'function': simplify_final_stop_sonorant_clusters},
    {'rule': 14000, 'description': 'No fricatives after affricates', 'function': no_fricatives_after_affricates},
    {'rule': 14001, 'description': 'No affricates after fricatives', 'function': no_affricates_after_fricatives},
    {'rule': 14005, 'description': 'Epenthesis and metathesis /ʃd/ → [ɬt]', 'function': shd_to_lht},
    {'rule': 14006, 'description': 'Voiceless glottal fricative h to pharyngeal fricative ħ', 'function': h_to_ħ},
]

# Function to apply all sound changes
def apply_sound_changes(year_and_word, max_year=None):
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
        
        word = change['function'](unmark_stress(word))
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
        'ħ': r'h',
    }
    for roman_char, latex_char in replacements.items():
        word = word.replace(roman_char, latex_char)
    return word

def get_dictionary_csv(word_after_changes, translation, stress, rom, pos, notes, roots):
    # Create a display IPA with syllable dots, but do not use dots in sound changes.
    display_ipa = dotted_with_stress(unmark_stress(word_after_changes))
    csv_lines = []
    csv_lines.append(f"{translation.strip()},{rom},/{display_ipa}/,{pos},{roots}")
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
    for f in ['compounds.csv', 'calendar.csv']:
        print(f'Loading compounds from {f}')
        with open(f, 'r', encoding='utf-8') as file:
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
        csv_history = csv_history.replace("+", " + ")
        words = csv_history.strip().split(',')[0].split('/')
        csv_history = csv_history.replace("/", " / ")
        if len(words) > 1:
            for w in words:
                parts = csv_history.strip().split(',')
                new_csv = f'{w.strip()},' + ','.join(parts[1:])
                # add to identical column
                new_csv = new_csv.rsplit(',',0)[0] +","+ " / ".join(words)
                expanded_csv_histories.append(new_csv)
        else:
            expanded_csv_histories.append(csv_history.strip()+',_')
            
    # sort csv_histories by the first line's final word, numbers at end of list, pos=CASE at end of list 
    def sort_dict(x):
        first_line = x.splitlines()[0]
        first_word = first_line.split('","')[0].strip('"').lower()
        pos = first_line.split(',')[3].strip('"')
        # if pos is 'case' or 'ps' or 'ns', put at end
        if pos in ['CASE', 'CLASS', 'PLURAL', 'MOOD', 'VOICE', 'ASPECT', 'PLACEHOLDER']:
            return 'zzz' + first_word
        if not first_word[0].isdigit():
            return first_word
        else:
            return 'zzzz' + first_word
    expanded_csv_histories = sorted(expanded_csv_histories, key=sort_dict)
    # remove columns 'POS' and 'Identical' from csv histories (columns 3 and 5)
    expanded_csv_histories = [','.join(line.split(',')[:-1]) for line in expanded_csv_histories]
    expanded_csv_histories = [','.join(line.split(',')[:3]+line.split(',')[4:]) for line in expanded_csv_histories]
   
    
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
    pages_filename='site/'+csv_filename
    for fname in [csv_filename, pages_filename]:
        with open(fname, 'w', encoding='utf-8') as file:
            file.write('English,Tovian,IPA,Roots\n')
            for csv_history in expanded_csv_histories:
                file.write(csv_history + '\n\n')
            
        
    if args.interactive:
        print("Interactive mode enabled. Type 'q' to quit.")
        while True:
            user_input = input("Enter a word or definition: ").strip().lower()
            if user_input == 'q':
                break
            dict_lower_keys = {k.lower(): v for k,v in interactive_dict.items()}
            if user_input in dict_lower_keys.keys():
                final_word, pos, history, rom, stress, note = dict_lower_keys[user_input]
                print(f"Final Word: {final_word}, POS: {pos}, Romanization: {rom}, Stress: {stress}")
                if note!="_" and note:
                    print(f"Note: {note}")
                for rule, word in history:
                    print(f'{rule}: {mark_stress(word)}')
            else:
                print("Word not found in the dictionary. 'q' to quit.")

if __name__ == "__main__":
    main()
    