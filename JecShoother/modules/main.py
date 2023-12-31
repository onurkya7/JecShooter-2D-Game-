import pygame
import os
import random
import csv
import button
from pygame import mixer

pygame.init()
mixer.init()

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('')

#kare hızı ayarlama
clock = pygame.time.Clock()
FPS = 144

#oyun değerlerini tanımlama
GRAVITY = 0.75
SCROLL_THRESH = 1000
ROWS = 20
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 38
MAX_LEVELS = 3
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False
game_finish = False

#oyuncu eylem değişkenleri tanımlama
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False


#müzik ve ses yükleme
pygame.mixer.music.load('audio/audio_music2.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)
jump_fx = pygame.mixer.Sound('audio/audio_jump.wav')
jump_fx.set_volume(0.06)
shot_fx = pygame.mixer.Sound('audio/audio_shot.wav')
shot_fx.set_volume(0.06)
grenade_fx = pygame.mixer.Sound('audio/audio_grenade.wav')
grenade_fx.set_volume(0.06)

#button resmi yükleme
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()
mc_img = pygame.image.load('img/mc_btn.png').convert_alpha()
#arkaplan yükleme
back_img = pygame.image.load('img/Background/back.jpg').convert_alpha()
clouds_1_img = pygame.image.load('img/Background/clouds_1.png').convert_alpha()
clouds_2_img = pygame.image.load('img/Background/clouds_2.png').convert_alpha()
ground_1_img = pygame.image.load('img/Background/ground_1.png').convert_alpha()
ground_2_img = pygame.image.load('img/Background/ground_2.png').convert_alpha()
ground_3_img = pygame.image.load('img/Background/ground_3.png').convert_alpha()
rocks_img = pygame.image.load('img/Background/rocks.png').convert_alpha()
sky_img = pygame.image.load('img/Background/sky.png').convert_alpha()
#fayansları gösterme
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/Tile/{x}.png.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)
#mermi
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
#el bombası
grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()
#ödül kutuları
health_box_img = pygame.image.load('img/icons/h.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/a.png').convert_alpha()
grenade_box_img = pygame.image.load('img/icons/g.png').convert_alpha()
item_boxes = {
    'Health'    : health_box_img,
    'Ammo'      : ammo_box_img,
    'Grenade'   : grenade_box_img
}

#renk tanımlama
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

#yazı tipi tanımlama
font = pygame.font.SysFont('Futura', 30)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
	screen.fill(BG)
	width = sky_img.get_width()
	for x in range(8):
		screen.blit(sky_img, ((x * width) -bg_scroll * 0.5, SCREEN_HEIGHT - sky_img.get_height() - 75 ))
		screen.blit(clouds_1_img, ((x * width) -bg_scroll * 0.8, SCREEN_HEIGHT - clouds_1_img.get_height() - 75 ))
		screen.blit(rocks_img, ((x * width) -bg_scroll * 0.6, SCREEN_HEIGHT - rocks_img.get_height() - 75 ))
		screen.blit(clouds_2_img, ((x * width) -bg_scroll * 0.8, SCREEN_HEIGHT - clouds_2_img.get_height() - 75 ))
		screen.blit(ground_1_img, ((x * width) -bg_scroll * 0.9, SCREEN_HEIGHT - ground_1_img.get_height() - 75 ))
		screen.blit(ground_2_img, ((x * width) -bg_scroll * 0.9, SCREEN_HEIGHT - ground_2_img.get_height() - 75 ))
		screen.blit(ground_3_img, ((x * width) -bg_scroll * 0.9, SCREEN_HEIGHT - ground_3_img.get_height() - 0 ))


#seviyeyi sıfırlama işlevi
def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()
    trap_group.empty()

    
#boş fayans listesi oluşturma
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data


class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        #yapay zekaya ait değişkenler
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0
        
        #oyuncular için resim yükleme
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            #geçici resim listesini sıfırlama
            temp_list = []
            #klasördeki dosya sayısını sayma
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()


    def update(self):
        self.update_animation()
        self.check_alive()
        #bekleme süresini güncelleme
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1


    def move(self, moving_left, moving_right):
        
        #hareket değişkenlerini sıfırla
        screen_scroll = 0
        dx = 0
        dy = 0

        #sola veya sağa hareket ediyorsanız hareket değişkenleri atama
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        #zıplama
        if self.jump == True and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        #yerçekimi
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        #çarpışmayı kontrol et
        for tile in world.obstacle_list:
            #x yönünde çarpışmayı kontrol et
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                #yapay zeka bir duvara çarptıysa, onu geri çevirin
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            #y yönünde çarpışmayı kontrol edin
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                #check if below the ground, i.e. jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                #yerden yüksekte olup olmadığını kontrol edin, yani düşmek
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom


        #zehire düşme kontrolü
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0
            
        #tuzağa düşme kontrolü
        if pygame.sprite.spritecollide(self, trap_group, False):
            self.health = 0
        
        
        #çıkış ile çarpışmayı kontrol edin
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        #haritadan düşüp düşmediğini kontrol et
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0


        #ekranın kenarlarından çıkıp çıkmadığını kontrol edin
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        #dikdörtgen konumunu güncelle
        self.rect.x += dx
        self.rect.y += dy

        #oyuncu pozisyonuna göre kaydırma güncellemesi
        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH )\
                or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete



    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            #cephaneyi azaltmak
            self.ammo -= 1
            shot_fx.play()


    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)#0: idle
                self.idling = True
                self.idling_counter = 50
            #Y.Z'nın oyuncunun yakınında olup olmadığını kontrol edin
            if self.vision.colliderect(player.rect):
                #koşmayı bırak ve oyuncuyla yüzleş
                self.update_action(0)#0: idle
                #ateş atme
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)#1: run
                    self.move_counter += 1
                    #düşman hareket ettikçe yapay zekayı güncelle
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        #kaydırma
        self.rect.x += screen_scroll


    def update_animation(self):
        #güncelleme animasyonu
        ANIMATION_COOLDOWN = 100
        #geçerli çerçeveye bağlı olarak resmi güncelle
        self.image = self.animation_list[self.action][self.frame_index]
        #son güncellemeden bu yana yeterli zaman geçip geçmediğini kontrol edin
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #animasyon bittiyse, sıfırlamayı en başa döndürün
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0



    def update_action(self, new_action):
        #yeni eylemin öncekinden farklı olup olmadığını kontrol etme
        if new_action != self.action:
            self.action = new_action
            #animasyon ayarlarını güncelle
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()



    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)


    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        #seviye veri dosyasındaki her bir değeri yineleme
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 21:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 22 and tile <= 23:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile == 28:
                        trap = Trap(img, x * TILE_SIZE, y * TILE_SIZE)
                        trap_group.add(trap)
                
                    elif tile >= 25 and tile <= 27:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 32:#oyuncu oluşturma
                        player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 0.06, 5, 20, 5)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 33:#düşman oluşturma
                        enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE, 0.07, 2, 20, 0)
                        enemy_group.add(enemy)
                    elif tile == 34:#cephane kutusu oluşturma
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 36:#el bombası kutusu
                        item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 35:#can puanı kutusu
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 29:#diğer levele geçiş tabelası
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)

        return player, health_bar


    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Trap(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))  

    def update(self):
        self.rect.x += screen_scroll
        
        
class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


    def update(self):
        #kaydırma
        self.rect.x += screen_scroll
        #oyuncunun kutuyu alıp almadığını kontrol edin
        if pygame.sprite.collide_rect(self, player):
            #ne tür bir kutu olduğunu kontrol et
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades += 3
            #kutuyu sil
            self.kill()


class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        #yeni sağlık güncelleme
        self.health = health
        #sağlık oranını hesapla
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        #mermiyi hareket ettir
        self.rect.x += (self.direction * self.speed) + screen_scroll
        #merminin ekrandan çıkıp çıkmadığını kontrol edin
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        #seviye ile çarpışmayı kontrol edin
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        #karakterlerle çarpışmayı kontrol et
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 8
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 30
                    self.kill()



class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        #harita ile çarpışmayı kontrol edin
        for tile in world.obstacle_list:
            #duvarlarla çarpışmayı kontrol et
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            #y yönünde çarpışmayı kontrol edin
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                #yerin altında olup olmadığını kontrol edin
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                #yerden yüksekte olup olmadığını kontrol edin, yani düşüyor
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom 


        #el bombası pozisyonunu güncelle
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        #countdown timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)
            #yakındaki herkese zarar verme
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50



class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 21):
            img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0


    def update(self):
        #kaydırma
        self.rect.x += screen_scroll

        EXPLOSION_SPEED = 4
        #patlama animasyonunu güncelleme
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            #animasyon tamamlandıysa patlamayı silin
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]


class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0


    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:#tüm ekran kararıyor
            pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.colour, (0, SCREEN_HEIGHT // 2 +self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.direction == 2:#dikey ekran kararıyor
            pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True

        return fade_complete


#ekran kararmaları oluştur
intro_fade = ScreenFade(1, BLACK, 14)
death_fade = ScreenFade(2, PINK, 14)



#buton oluşturma
start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT // 2 - 150, restart_img, 3)
mc_button = button.Button(SCREEN_WIDTH // 2 - 320, SCREEN_HEIGHT // 2 - 250, mc_img, 0.5)
exitt_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 300, exit_img, 1)


#hareketli grafik grupları oluşturma
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
trap_group = pygame.sprite.Group()


#boş fayans listesi oluştur
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
#seviye verilerini yükleyin ve dünya yaratın
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)



run = True
while run:

    clock.tick(FPS)

    if start_game == False:
        #menu çizimi
        screen.fill(RED)
        #butonları ekleme
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            run = False
    else:
        #arkaplanı ekleme
        draw_bg()
        #harita çizimi
        world.draw()
        #oyuncu can puanını çizme
        health_bar.draw(player.health)
        #cephane
        draw_text('AMMO: ', font, WHITE, 10, 35)
        for x in range(player.ammo):
            screen.blit(bullet_img, (90 + (x * 15), 40))
        #el bombası
        draw_text('GRANADE: ', font, WHITE, 10, 60)
        for x in range(player.grenades):
            screen.blit(grenade_img, (120 + (x * 20), 60))


        player.update()
        player.draw()

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        #grupları güncelle ve çiz
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        trap_group.update()
        exit_group.update()
        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        trap_group.draw(screen)
        exit_group.draw(screen)
        

        #introyu göster
        if start_intro == True:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0


        #oyuncu işlemlerini güncelle
        if player.alive:
            #mermi sıkmak
            if shoot:
                player.shoot()
            #el bombası atmak
            elif grenade and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),\
                            player.rect.top, player.direction)
                grenade_group.add(grenade)
                #el bombası azaltmak
                player.grenades -= 1
                grenade_thrown = True
            if player.in_air:
                player.update_action(2)#2: zıplama
            elif moving_left or moving_right:
                player.update_action(1)#1: koşma
            else:
                player.update_action(0)#0: boşta
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            #oyuncunun seviyeyi tamamlayıp tamamlamadığını kontrol et
            
            if level_complete:          
                if level <= MAX_LEVELS:
                  start_intro = True
                  level += 1
                  bg_scroll = 0
                  world_data = reset_level()
                
                
                #seviye verilerini yükleyin ve dünya yaratın
                  with open(f'level{level}_data.csv', newline='') as csvfile:
                      reader = csv.reader(csvfile, delimiter=',')
                      for x, row in enumerate(reader):
                          for y, tile in enumerate(row):
                              world_data[x][y] = int(tile)
                  world = World()
                  player, health_bar = world.process_data(world_data)
                
                else: 
                   if game_finish == False:                     
                       screen.fill(BLACK)
                       mc_button.draw(screen)
                       draw_text('Developed by onurkya_', font, WHITE, 10, 10)
                       if exitt_button.draw(screen):
                           run = False
                  
                
             
        else:
            screen_scroll = 0
            if death_fade.fade():
                if exit_button.draw(screen):
                    run = False
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    world_data = reset_level()
                    #seviye verilerini yükleyin ve dünya yaratın
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)


    for event in pygame.event.get():
        #oyundan çık
        if event.type == pygame.QUIT:
            run = False
        #klavye tuşlarına basma
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_q:
                grenade = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                run = False


        #klavye tuşlarından elini çekme
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False


    pygame.display.update()

pygame.quit()