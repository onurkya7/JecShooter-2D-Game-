import pygame

import csv

import button

import pickle

pygame.init()

clock = pygame.time.Clock()
FPS = 144

#oyun penceresi
SCREEN_WIDTH = 1320
SCREEN_HEIGHT = 980
LOWER_MARGIN = 100
SIDE_MARGIN = 600

screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption('Level Düzenleyici')


#oyun veri tanımı
ROWS = 20
MAX_COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 38
level = 0
current_tile = 0
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1


#resim yüklenmesi
back_img = pygame.image.load('img/Background/back.jpg').convert_alpha()
clouds_1_img = pygame.image.load('img/Background/clouds_1.png').convert_alpha()
clouds_2_img = pygame.image.load('img/Background/clouds_2.png').convert_alpha()
ground_1_img = pygame.image.load('img/Background/ground_1.png').convert_alpha()
ground_2_img = pygame.image.load('img/Background/ground_2.png').convert_alpha()
ground_3_img = pygame.image.load('img/Background/ground_3.png').convert_alpha()
rocks_img = pygame.image.load('img/Background/rocks.png').convert_alpha()
sky_img = pygame.image.load('img/Background/sky.png').convert_alpha()

#fayans listesi verisini ekrana yansıtma
img_list = []
for x in range(TILE_TYPES):
	img = pygame.image.load(f'img/tile/{x}.png.png').convert_alpha()
	img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	img_list.append(img)

save_img = pygame.image.load('img/save_btn.png').convert_alpha()
load_img = pygame.image.load('img/load_btn.png').convert_alpha()


#renk tanımı
GREEN = (144, 201, 120)
WHITE = (255, 255, 255)
RED = (200, 25, 25)

#define font
font = pygame.font.SysFont('Futura', 30)

#boş fayans oluşturma
world_data = []
for row in range(ROWS):
	r = [-1] * MAX_COLS
	world_data.append(r)

#zemin oluşumu
for tile in range(0, MAX_COLS):
	world_data[ROWS - 1][tile] = 19


#ekranda fonk. gösterimi
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))


#arkaplan çizimi fonk. oluşturma
def draw_bg():
	screen.fill(RED)
	width = sky_img.get_width()
	for x in range(7):
		screen.blit(sky_img, ((x * width) -scroll * 0.5, SCREEN_HEIGHT - sky_img.get_height() - 75 ))
		screen.blit(clouds_1_img, ((x * width) -scroll * 0.8, SCREEN_HEIGHT - clouds_1_img.get_height() - 75 ))
		screen.blit(rocks_img, ((x * width) -scroll * 0.6, SCREEN_HEIGHT - rocks_img.get_height() - 75 ))
		screen.blit(clouds_2_img, ((x * width) -scroll * 0.8, SCREEN_HEIGHT - clouds_2_img.get_height() - 75 ))
		screen.blit(ground_1_img, ((x * width) -scroll * 0.9, SCREEN_HEIGHT - ground_1_img.get_height() - 75 ))
		screen.blit(ground_2_img, ((x * width) -scroll * 0.9, SCREEN_HEIGHT - ground_2_img.get_height() - 75 ))
		screen.blit(ground_3_img, ((x * width) -scroll * 0.9, SCREEN_HEIGHT - ground_3_img.get_height() - 0 ))
		
#çizgilerin oluşumu
def draw_grid():
	#dikey çizgiler
	for c in range(MAX_COLS + 1):
		pygame.draw.line(screen, WHITE, (c * TILE_SIZE - scroll, 0), (c * TILE_SIZE - scroll, SCREEN_HEIGHT))
	#yatay çizgiler
	for c in range(ROWS + 1):
		pygame.draw.line(screen, WHITE, (0, c * TILE_SIZE), (SCREEN_WIDTH, c * TILE_SIZE))


#function for drawing the world tiles
def draw_world():
	for y, row in enumerate(world_data):
		for x, tile in enumerate(row):
			if tile >= 0:
				screen.blit(img_list[tile], (x * TILE_SIZE - scroll, y * TILE_SIZE))



#butonları oluşturma
save_button = button.Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT + LOWER_MARGIN - 50, save_img, 1)
load_button = button.Button(SCREEN_WIDTH // 2 + 200, SCREEN_HEIGHT + LOWER_MARGIN - 50, load_img, 1)
#buton listesi yapma
button_list = []
button_col = 0
button_row = 0
for i in range(len(img_list)):
	tile_button = button.Button(SCREEN_WIDTH + (75 * button_col) + 50, 75 * button_row + 50, img_list[i], 1)
	button_list.append(tile_button)
	button_col += 1
	if button_col == 3:
		button_row += 1
		button_col = 0


run = True
while run:

	clock.tick(FPS)

	draw_bg()
	draw_grid()
	draw_world()

	draw_text(f'Level: {level}', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 90)
	draw_text('Press UP or DOWN to change level', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 60)

	#verinin kaydı ve yüklenmesi
	if save_button.draw(screen):
		#save level data
		with open(f'level{level}_data.csv', 'w', newline='') as csvfile:
			writer = csv.writer(csvfile, delimiter = ',')
			for row in world_data:
				writer.writerow(row)
		#alternative pickle method
		#pickle_out = open(f'level{level}_data', 'wb')
		#pickle.dump(world_data, pickle_out)
		#pickle_out.close()
	if load_button.draw(screen):
		#levelin yüklenmesi
		#scroll la geriye gidilmesi (level)
		scroll = 0
		with open(f'level{level}_data.csv', newline='') as csvfile:
			reader = csv.reader(csvfile, delimiter = ',')
			for x, row in enumerate(reader):
				for y, tile in enumerate(row):
					world_data[x][y] = int(tile)
		#alternative pickle metod
		#world_data = []
		#pickle_in = open(f'level{level}_data', 'rb')
		#world_data = pickle.load(pickle_in)
				

	#fayans paneli ve fayans çizimi
	pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT))

	#fayans seçimi
	button_count = 0
	for button_count, i in enumerate(button_list):
		if i.draw(screen):
			current_tile = button_count

	#fayansı kırmızı alan içine alma
	pygame.draw.rect(screen, RED, button_list[current_tile].rect, 3)

	#harita kaydırılması
	if scroll_left == True and scroll > 0:
		scroll -= 5 * scroll_speed
	if scroll_right == True and scroll < (MAX_COLS * TILE_SIZE) - SCREEN_WIDTH:
		scroll += 5 * scroll_speed

	#yeni fayansların ekrana yansıması
	#farenin yerini ayarlama
	pos = pygame.mouse.get_pos()
	x = (pos[0] + scroll) // TILE_SIZE
	y = pos[1] // TILE_SIZE

	#kordinatlara göre fayansların yerini kontrol etme
	if pos[0] < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:
		#fayansların güncellenmesi
		if pygame.mouse.get_pressed()[0] == 1:
			if world_data[y][x] != current_tile:
				world_data[y][x] = current_tile
		if pygame.mouse.get_pressed()[2] == 1:
			world_data[y][x] = -1


	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		#klavye dokunma
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP:
				level += 1
			if event.key == pygame.K_DOWN and level > 0:
				level -= 1
			if event.key == pygame.K_LEFT:
				scroll_left = True
			if event.key == pygame.K_RIGHT:
				scroll_right = True
			if event.key == pygame.K_RSHIFT:
				scroll_speed = 5


		if event.type == pygame.KEYUP:
			if event.key == pygame.K_LEFT:
				scroll_left = False
			if event.key == pygame.K_RIGHT:
				scroll_right = False
			if event.key == pygame.K_RSHIFT:
				scroll_speed = 1


	pygame.display.update()

pygame.quit()