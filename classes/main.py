# main.py
import sys
import pygame
import networkx as nx
import time
import math


WIDTH, HEIGHT      = 900, 700
BG_COLOR           = (10, 10, 30)
NODE_COLOR         = (200, 200, 255)
ENTAIL_COLOR       = (100, 150, 255)
CONTRADICT_COLOR   = (255, 100, 100)
TEXT_COLOR         = (240, 240, 240)
NODE_RADIUS        = 25
FONT_SIZE          = 20


propositions = {

    "A" : "Pythons are grumpy",
    "B" : "Pythons & Cobras are distraught",
    "C" : "All snakes are always happy"



}



relations = [

    ("A", "B", "entail"),
    ("B", "C", "contradict"),
    ("A", "C", "contradict")


]


def build_graph(props, rels):
    G = nx.DiGraph()
    for pid, stmt in props.items():
        G.add_node(pid, text=stmt)
    for src, dst, typ in rels:
        G.add_edge(src, dst, rel=typ)
    return G

def compute_positions(G):
    raw = nx.spring_layout(G, scale=1.0)

    pos = {}
    for node, (x, y) in raw.items():
        px = int((x * (WIDTH/2 - 50)) + WIDTH/2)
        py = int((y * (HEIGHT/2 - 50)) + HEIGHT/2)
        pos[node] = (px, py)
    return pos


class InputBox:
    def __init__(self, x, y, w, h, font):
        self.rect   = pygame.Rect(x, y, w, h)
        self.color  = (50, 50, 70)
        self.text   = ""
        self.font   = font
        self.active = False
        self.done   = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.done = True
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if event.unicode.isprintable():
                    self.text += event.unicode

    def draw(self, screen):
        # box
        pygame.draw.rect(screen, self.color, self.rect)
        # text
        txt_surf = self.font.render(self.text, True, TEXT_COLOR)
        screen.blit(txt_surf, (self.rect.x + 5, self.rect.y + 5))

    def reset(self):
        self.text = ""
        self.done = False

# --- Main Loop ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Semantic Galaxy")
    clock  = pygame.time.Clock()
    font   = pygame.font.SysFont(None, FONT_SIZE)

    G         = build_graph(propositions, relations)
    positions = compute_positions(G)

    input_mode = None  # "node" or "edge"
    box = InputBox(50, HEIGHT - 60, WIDTH - 100, 40, font)

    running = True
    while running:
        mx, my = pygame.mouse.get_pos()
        t = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Toggle input modes
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n and not input_mode:
                    input_mode = "node"
                    box.active = True
                elif event.key == pygame.K_e and not input_mode:
                    input_mode = "edge"
                    box.active = True
                elif event.key == pygame.K_ESCAPE and input_mode:
                    input_mode = None
                    box.active = False
                    box.reset()

            # Pass events to input box
            box.handle_event(event)

        if box.done:
            line = box.text.strip()
            if input_mode == "node":
                if ":" in line:
                    nid, stmt = map(str.strip, line.split(":", 1))
                    if nid and stmt:
                        propositions[nid] = stmt
            elif input_mode == "edge":
                parts = line.split()
                if len(parts) == 3:
                    src, dst, typ = parts
                    if typ in ("entail", "contradict"):
                        relations.append((src, dst, typ))
            # rebuild graph + positions
            G = build_graph(propositions, relations)
            positions = compute_positions(G)
            # reset input
            input_mode = None
            box.active = False
            box.reset()

        # --- Drawing ---
        screen.fill(BG_COLOR)

        # Draw edges
        for u, v, data in G.edges(data=True):
            x1, y1 = positions[u]
            x2, y2 = positions[v]
            col = ENTAIL_COLOR if data["rel"] == "entail" else CONTRADICT_COLOR
            pygame.draw.line(screen, col, (x1, y1), (x2, y2), 3)

        # Draw nodes
        for node, data in G.nodes(data=True):
            x, y = positions[node]
            # check for incoming contradictions
            has_contra = any(G[u][node]["rel"] == "contradict" for u in G.predecessors(node))
            if has_contra:
                # flashing effect
                shine = (math.sin(t * 5) + 1) / 2
                col   = (
                    int(NODE_COLOR[0] + shine * (255 - NODE_COLOR[0])),
                    int(NODE_COLOR[1] * (1 - shine)),
                    int(NODE_COLOR[2] * (1 - shine))
                )
            else:
                col = NODE_COLOR

            pygame.draw.circle(screen, col, (x, y), NODE_RADIUS)
            # draw ID in center
            id_surf = font.render(node, True, BG_COLOR)
            w, h    = id_surf.get_size()
            screen.blit(id_surf, (x - w//2, y - h//2))

        # Draw instructions
        inst1 = font.render("Press N to add node (format: ID: statement)", True, TEXT_COLOR)
        inst2 = font.render("Press E to add edge (format: SRC DST [entail|contradict])", True, TEXT_COLOR)
        screen.blit(inst1, (20, 10))
        screen.blit(inst2, (20, 35))

        # Draw input box #~
        if box.active:
            box.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
