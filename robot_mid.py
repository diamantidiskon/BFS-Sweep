from collections import deque

# Αρχικοποίηση ορίων κόσμου και ορισμός των συμβόλων αυτού
rows, cols = 10, 10
empty, obst, item = ".", "#", "*"


def load_world(path):
    """Δέχεται ως όρισμα το δοθέν από τον χρήστη path
    και επιστρέφεται 2D list του κόσμου έπειτα από έλεγχο εγκυρότητάς του"""
    world = []
    # Οτιδήποτε έχει να κάνει με το άνοιγμα του αρχείου και εξαιρέσεις βάσει πιθανών λανθασμένων εισόδων του χρήστη
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                row = line.strip().split()
                world.append(row)
    except FileNotFoundError:
        print("Το αρχείο δεν βρέθηκε.")
    assert len(world) == rows and all(len(r)==cols for r in world) , ["Λάθος διαστάσεις world.txt"]
    valid = {empty, obst, item}
    for r in world:
        for s in r:
            assert s in valid, f"Άκυρο σύμβολο: {s}"
    return world


def print_world(world, r, c) -> None:
    """Εμφάνιση του κόσμου και της θέσης του ρομπότ σε αυτόν"""
    for i in range(rows):
        line = []
        for j in range(cols):
            line.append("R" if (i,j)==(r,c) else world[i][j])
        print(" ".join(line))
    print()


def in_bounds(r: int, c: int) -> bool:
    """Έλεγχος συντεταγμένων (r, c) ως προς την οριοθέτηση του κόσμου"""
    return 0 <= r < rows and 0 <= c < cols


def neighbors(world, r, c):
    """Εύρεση γειτόνων των δοθέντων συντεταγμένων του κόσμου"""
    for dr, dc in [(0,-1),(0,1),(-1,0),(1,0)]:
        nr, nc = r+dr, c+dc
        if in_bounds(nr, nc) and world[nr][nc] != obst:
            yield nr, nc


def bfs_path_to_nearest_item(world, start):

    """Στρατηγική BFS στο αμέσως επόμενο πλησιέστερο αντικείμενο"""

    queue = deque([start])
    parent = {start: None}
    path = []
    visited = ()

    # Επανάληψη για όσο υπάρχουν στην ουρά σημεία προς εξέταση
    while queue:
        position = queue.popleft()
        # Προσθήκη στα ήδη εξετασμένα σημεία του πλέγματος
        visited += (position,)
        if world[position[0]][position[1]] == item:
            # Σχηματισμός λίστας διαδρομής με σειρά από τον στόχο προς το αρχικό σημείο
            while position != start:
                path.append(position)
                position = parent[position]
            # Διακοπή της επανάληψης όταν βρεθεί αντικείμενο
            break
        for neighbor in neighbors(world, position[0], position[1]):
            if neighbor not in visited:
                # Για κάθε γειτονικό σημείο δημιουργία μονοσήμαντης σχέσης παιδιού->γονέα σε λεξικό
                # και προσθήκη του προς εξέταση
                parent[neighbor] = position
                queue.append(neighbor)

    # Επιστροφή της διαδρομής με σειρά από την αρχή προς τον στόχο
    return path[::-1]


def next_step_sweep(world, r, c, direction):
    """Στρατηγική sweep με επιστροφή του επόμενου σωστού βήματος ανάλογα της κατεύθυνσης
    και προειδοποίησης σε περίπτωση εμποδίου (Boolean)"""
    if direction == 1 and c == cols-1:
        return r+1 if is_valid(r+1,c) else r, c, -1, False
    if direction == -1 and c == 0:
        return r+1 if is_valid(r+1,c) else r, c, 1, False
    else:
        return (r, c+direction, direction, False) if world[r][c+direction] != obst else (r, c, direction, True)


def is_valid(y,x):
    """Έλεγχος εγκυρότητας σημείου του πλέγματος, με αξιοποίηση in_bounds"""
    world = load_world(file_path)
    return in_bounds(y, x) and world[y][x] != obst


def sweep_obstacle(r, c, direction):
    """Στρατηγική sweep σε περίπτωση εμποδίου, με σκοπό την παράκαμψή του"""
    # Δύο εναλλακτικές παράκαμψης, από πάνω ή από κάτω
    upp = (r-1, c)
    dow = (r+1, c)
    pathlist = {}
    direction3 = ()


    def searching(direction2):
        """Διερευνά την κατάλληλη διαδρομή προς προσπέραση του εμποδίου, βάσει της στρατηγικής sweep"""
        row, col = direction2[0], direction2[1]
        pathlist[direction2] = [(row, col)]

        # Έλεγχος αν επιτρέπεται να πάμε προς τα κάτω ή προς τα πάνω
        if is_valid(row,col) and is_valid(row,col+direction):
            row, col = row, col+direction
            pathlist[direction2] += [(row, col)]

            # Επανάληψη για όσο δεν μπορεί το ρομπότ να επιστρέψει στη σειρά που σάρωνε όταν συνάντησε το πρώτο εμπόδιο
            while (not is_valid(row - 1, col)) if direction2 == dow else (not is_valid(row + 1, col)):
                if is_valid(row, col + direction):
                    row, col = row, col + direction
                    pathlist[direction2] += [(row, col)]
                else:

                    # Αν συναντήσει το ρομπότ εμπόδιο στην εναλλακτική διαδρομή, ξανακαλείται η sweep_obstacle
                    pathlist[direction3], row, col = sweep_obstacle(row, col, direction)
                    pathlist[direction2] += pathlist[direction3]
            pathlist[direction2] += [(row-1, col)] if direction2 == dow else [(row+1, col)]

            # Ανάλογα με την κατεύθυνση (πάνω ή κάτω) σε περίπτωση που έχουν προσπεραστεί εμπόδια που σχηματίζουν μορφή
            # σκάλας εκτελείται επιστροφή του ρομπότ το πλησιέστερο δυνατό στο αρχικό σημείο πριν τη σκάλα
            if is_valid(row-1,col-direction) and direction2==dow:
                pathlist[direction2] += [(row - 1, col-direction)]
                row, col = row, col - direction
            elif is_valid(row+1,col-direction) and direction2==upp:
                pathlist[direction2] += [(row + 1, col-direction)]
                row, col = row, col - direction
            return pathlist[direction2], row-1 if direction2 == dow else row+1, col
        else:

            # Σε περίπτωση που απαγορεύεται η προσπέραση από κάτω επιλέγεται η προσπέραση από πάνω
            return searching(upp)


    # Επιστροφή της συνάρτησης searching
    return searching(dow)


def run(strategy="BFS", verbose_every=10):

    """Η βασική συνάρτηση του προγράμματος, η οποία αξιοποιεί όλες τις υπόλοιπες
        για να υλοποιηθεί το πρόγραμμα, βάσει της δοθείσας ως όρισμα από τον χρήστη στρατηγικής"""

    world = load_world(file_path)
    r, c = 0, 0
    direction = 1
    score, steps = 0, 0
    alternative_sweep = False
    all_items_collected = False
    path_to_new_item = deque([])
    alternative_path = deque([])

    # Επανάληψη για όσο δεν έχει ξεπεραστεί το φράγμα των επιτρεπόμενων βημάτων
    while steps < 80:
        show = True

        # Σε περίπτωση αντικειμένου, αύξηση του σκορ και κλήση της bfs_next_step ενδείκνυνται από τη στρατηγική
        if world[r][c] == item or (r,c)==(0,0):
            print(f"Συλλέχθηκε αντικείμενο στη θέση {r,c}" if (r,c)!=(0,0) else "")
            world[r][c] = empty
            if strategy.upper()=="BFS":
                path_to_new_item = deque(bfs_path_to_nearest_item(world, (r,c)))
            score += 1 if (r,c)!=(0,0) else 0

            # Τερματισμός σε περίπτωση συλλογής όλων των αντικειμένων
            if not any(item in row for row in world):
                all_items_collected = True
                break

        # Επόμενο βήμα για την BFS, αν αυτή είναι η στρατηγική
        if strategy.upper() == "BFS":
            if path_to_new_item!=deque([]):
                new = path_to_new_item.popleft()
                r, c = (new[0], new[1])
            else:
                break
        else:

            # Αν η στρατηγική είναι η sweep, γίνεται έλεγχος για εμπόδια και
            # γίνεται το επόμενο βήμα με την κλασσική sweep ή καλείται η εναλλακτική διαδρομή σε περίπτωση εμποδίου
            if not alternative_sweep:
                r, c, direction, obstacle = next_step_sweep(world, r, c, direction)
                if obstacle:
                    alternative_path, k, l = sweep_obstacle(r, c, direction)
                    alternative_path = deque(alternative_path)
                    alternative_sweep, show = True, False
                    steps -= 1
            else:

                # Επανάληψη για όσο η ακολουθία βημάτων ανήκει στην εναλλακτική διαδρομή
                if alternative_path:
                    step_of_path = alternative_path.popleft()
                    r, c = step_of_path[0], step_of_path[1]
                else:
                    steps-=1
                    alternative_sweep, show = False, False
        steps += 1

        # Ενημέρωση του χρήστη μέσω εμφάνισης στο τερματικό για τα στατιστικά του παιχνιδιού με καθορισμένη συχνότητα
        if verbose_every and steps % verbose_every == 0:
            print(f"Step: {steps} | Position=({r},{c}) | Score={score} | Strategy={strategy}")
        if show:
            print_world(world, r, c)

    # Τελική ενημέρωση για την τελική επίδοση του ρομπότ στο δοθέν πλέγμα και του λόγου τερματισμού
    print(f"Τελικό σκορ: {score}, Βήματα: {steps}, Στρατηγική: {strategy}")
    print("Το παιχνίδι τερματίστηκε επειδή " + ("συλλέχθηκαν όλα τα αντικείμενα"
          if all_items_collected else "συμπληρώθηκαν τα επιτρεπόμενα βήματα"
          if steps == 80 else "το ρομπότ εγκλωβίστηκε ανάμεσα σε εμπόδια"))


# Εισαγωγή του αρχείου και της επιθυμητής στρατηγικής από τον χρήστη
file_path = input("Δώσε το όνομα ή τη διαδρομή του αρχείου world.txt: ")
run(input("Δώσε την επιθυμητή στρατηγική (BFS ή sweep): "))