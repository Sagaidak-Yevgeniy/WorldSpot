import pygame

from src.game import Game
from src.settings import FPS, HEIGHT, TITLE, WIDTH


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    game = Game(screen)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_event(event)
        game.update(dt)
        game.draw()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
