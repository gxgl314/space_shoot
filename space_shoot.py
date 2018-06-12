import sys, random, math, pygame
from pygame.locals import *
from os import path

pygame.mixer.pre_init(44100, -16,2, 2048)
pygame.mixer.init()
pygame.init()

class Player(pygame.sprite.Sprite):
	"""docstring for Player"""
	def __init__(self):
		super(Player, self).__init__()		
		self.image = pygame.transform.flip(player_img,False, True)
		self.image = pygame.transform.scale(self.image,(80,60))
		self.rect = self.image.get_rect()
		self.rect.centerx = WIDTH/2
		self.rect.bottom = HEIGHT
		self.vx = 5
		self.lifes = 3
		self.hp = 100
		self.score = 0
		self.add_scores = 0 
		self.hideden = False
		self.hide_time = 0
		self.is_missile_firing = False
		self.start_missile_time = 0
		self.last_missile_time = 0
	def reinit(self):
		self.rect.centerx = WIDTH/2
		self.rect.bottom = HEIGHT
		self.vx = 5
		self.lifes = 3
		self.hp = 100
		self.score = 0
		self.add_scores = 0 
		self.hideden = False
		self.hide_time = 0
		self.is_missile_firing = False
		self.start_missile_time = 0
		self.last_missile_time = 0
	def update(self):
		key_state = pygame.key.get_pressed()
		if key_state[pygame.K_LEFT]:
			self.rect.x -= self.vx
			if self.rect.centerx < 0:
				self.rect.centerx = 0
		if key_state[pygame.K_RIGHT]:
			self.rect.x += self.vx
			if self.rect.centerx > WIDTH:
				self.rect.centerx = WIDTH
		now = pygame.time.get_ticks()
		if self.hideden and now - self.hide_time > HIDE_PLAYER_INTERVAL:
			self.rect.centerx = WIDTH/2
			self.rect.bottom = HEIGHT
			self.hideden = False
		if self.is_missile_firing:
			if now - self.start_missile_time > MISSILE_LIFE_TIME:
				self.is_missile_firing = False
			else:
				if now - self.last_missile_time > MISSILE_INTERVAL:
					missile = Missile(self.rect.center)
					missiles.add(missile) 
					self.last_missile_time = now

		if self.lifes <=0:
			self.hp = 0
			self.kill()
		# screen.blit(self.image, self.rect)
	def shoot(self):
		bullet = Bullet(self.rect.centerx, self.rect.centery)
		bullets.add(bullet)
		shoot_sound.play()
	def fire_missile(self):
		self.is_missile_firing = True
		self.start_missile_time = pygame.time.get_ticks()
		
	def be_hit(self, reduce_hp):
		global game_state
		self.hp -= reduce_hp
		if self.hp <= 0:
			self.lifes -= 1;
			if self.lifes <= 0:
				game_state = 2
				self.kill()
			else:
				self.hide()
				self.hp = 100
			print("plarer lifes:{},hp:{}, game_state:{}".format(self.lifes,self.hp, game_state))
	def hide(self):
		self.hideden = True
		self.rect.y = -100
		self.hide_time = pygame.time.get_ticks()

	def add_score(self, score):
		self.score += score
		self.add_scores = score
		

class Enemy(pygame.sprite.Sprite):
	"""docstring for Enemy"""
	def __init__(self):
		super(Enemy, self).__init__()
		img_width = random.randint(20,110)
		self.ori_image = pygame.transform.scale(enemy_img,(img_width,img_width))
		self.image = self.ori_image
		self.rect = self.image.get_rect()
		self.rect.x = random.randint(0, WIDTH)
		self.rect.bottom = 0
		self.vx = random.randint(-2, 2)
		self.vy = random.randint(2,5)
		self.last_time = pygame.time.get_ticks()
		self.rotate_speed = random.randint(-5,5)
		self.rotate_angle = 0
		self.radius = img_width/2
	def reinit(self):		
		self.rect.x = random.randint(0, WIDTH)
		self.rect.bottom = 0
		self.last_time = pygame.time.get_ticks()
		self.rotate_speed = random.randint(-5,5)
		self.rotate_angle = 0
	def update(self):
		self.rect.x += self.vx
		self.rect.y += self.vy
		self.rotate()
		if self.rect.y > HEIGHT:
			enemy = Enemy()
			enemys.add(enemy)
			self.kill()
	def rotate(self):
		now = pygame.time.get_ticks()
		if now - self.last_time > 30:
			self.last_time = now
			self.rotate_angle = (self.rotate_angle + self.rotate_speed )% 360
			old_center = self.rect.center
			self.image = pygame.transform.rotate(self.ori_image, self.rotate_angle)
			self.rect = self.image.get_rect()
			self.rect.center = old_center

class Explosion(pygame.sprite.Sprite):
	"""docstring for Explosion"""
	def __init__(self, center):
		super(Explosion, self).__init__()
		self.image = explosion_animation[0]
		self.rect = self.image.get_rect()
		self.rect.center = center
		self.frame = 0
		self.last_time = pygame.time.get_ticks()
		explosion_sound.play()
	def update(self):
		now = pygame.time.get_ticks()
		if now - self.last_time > 60:			
			if self.frame < len(explosion_animation):
				self.image = explosion_animation[self.frame]
				self.frame += 1
				self.last_time = now
			else:
				self.kill()
			pass

class Bullet(pygame.sprite.Sprite):
	"""docstring for Bullet"""
	def __init__(self, x, y):
		super(Bullet, self).__init__()
		self.image = pygame.transform.scale(bullet_img, (5,23))
		self.rect = self.image.get_rect()
		self.rect.centerx = x
		self.rect.centery = y
	def update(self):
		self.rect.y -= 10
		if self.rect.y < -10:
			self.kill()

class Missile(pygame.sprite.Sprite):
	"""docstring for Missile"""
	def __init__(self, center):
		super(Missile, self).__init__()
		self.image = missile_img
		self.rect = self.image.get_rect()
		self.rect.center = center
	def update(self):
		self.rect.y -= 5
		if(self.rect.bottom < 0):
			self.kill()
		

class Powerup(pygame.sprite.Sprite):
	"""docstring for Powerup"""
	def __init__(self, center):
		super(Powerup, self).__init__()
		powerup_random = random.random()
		if powerup_random > 0.8:
			self.type = 'add_life'
		elif powerup_random > 0.5:
			self.type = 'add_missile'
		else:
			self.type = 'add_hp'
		self.image = powerup_imgs[self.type]
		self.rect = self.image.get_rect()
		self.rect.centerx = random.randint(20,WIDTH-20)
		self.rect.bottom = 0

	def update(self):
		self.rect.y += 3
		if self.rect.top > HEIGHT:
			self.kill()
		

def draw_ui():
	img_rect = player_img_small.get_rect()
	img_rect.x = 10
	img_rect.y = 10
	for i in range(player.lifes):
		screen.blit(player_img_small, img_rect)
		img_rect.x += img_rect.width + 10
	pygame.draw.rect(screen,(255,0,0), (10,40,player.hp,15))
	pygame.draw.rect(screen,(255,255,255), (10,40,100,15),2)
	draw_text(str(int(player.score)), screen, (0,255,0),50,60)
	draw_text(str(player.add_scores), screen, (255,255,255),50,90)

def draw_text(text, surface, color, x, y, fontsize = 20, fontname = 'arial'):
	fontname = pygame.font.match_font(fontname)
	font = pygame.font.Font(fontname, fontsize)
	text_surface = font.render(text,True, color)
	text_rect = text_surface.get_rect()
	text_rect.midtop = (x,y)
	surface.blit(text_surface, text_rect)


def show_menu(state):
	global game_state, screen

	screen.blit(background_img,background_rect)

	draw_text('Space Shooter', screen, WHITE, WIDTH/2, 100, fontsize = 40)
	draw_text('Press ESC Key to quit', screen, RED, WIDTH/2, 300,fontsize = 20)
	
	if state == 2:
		draw_text('Press SPACE Key to restart', screen, GREEN, WIDTH/2, 350,fontsize = 20)
		draw_text('Score',screen, WHITE, WIDTH/2, 400, fontsize = 60)
		draw_text(str(int(player.score)),screen, GREEN, WIDTH/2, 500, fontsize = 60)
	else:
		draw_text('Press SPACE Key to start', screen, GREEN, WIDTH/2, 350,fontsize = 20)

	event_list = pygame.event.get()
	for event in event_list:
		if event.type == pygame.QUIT:
			pygame.quit()
			quit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				pygame.quit()
				quit()
			if event.key == pygame.K_SPACE:
				game_state = 1
				if state == 2:
					player.reinit()
					for enemy in enemys:
						enemy.reinit()
					for bullet in bullets:
						bullet.kill()
				pass
	pygame.display.update()


WIDTH, HEIGHT = 480, 800
MISSILE_LIFE_TIME = 10000
MISSILE_INTERVAL = 1000
HIDE_PLAYER_INTERVAL = 1000
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)

framerate = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("星空")

game_state = 0

sound_dir = path.join(path.dirname(__file__), 'sound')
shoot_sound = pygame.mixer.Sound(path.join(sound_dir, 'shoot.wav'))
explosion_sound = pygame.mixer.Sound(path.join(sound_dir, 'explosion.wav'))
background_sound = pygame.mixer.music.load(path.join(sound_dir, 'background.ogg'))

image_dir = path.join(path.dirname(__file__), 'img')
background_dir = path.join(image_dir, 'background.png')
background_img = pygame.image.load(background_dir).convert_alpha()
background_rect = (0,0)
ship_dir = path.join(image_dir, 'space_ship.png')
player_img = pygame.image.load(ship_dir).convert_alpha()
player_img_small = pygame.transform.scale(player_img, (26,20))
bullet_dir = path.join(image_dir, 'space_bullet.png')
bullet_img = pygame.image.load(bullet_dir).convert()
meteor_dir = path.join(image_dir, 'space_meteor.png')
enemy_img = pygame.image.load(meteor_dir).convert_alpha()
missile_dir = path.join(image_dir, "missile.png")
missile_img = pygame.image.load(missile_dir).convert_alpha()


powerup_imgs = {}
powerup_add_hp_dir = path.join(image_dir, 'gen_red.png')
powerup_imgs['add_hp'] = pygame.image.load(powerup_add_hp_dir).convert_alpha()
powerup_add_life_dir = path.join(image_dir, 'heartFull.png')
powerup_imgs['add_life'] = pygame.image.load(powerup_add_life_dir).convert_alpha()
powerup_add_missile_dir = path.join(image_dir, 'gen_yellow.png')
powerup_imgs['add_missile'] = pygame.image.load(powerup_add_missile_dir).convert_alpha()


explosion_animation = []
for i in range(9):
	explosion_dir = path.join(image_dir, "regularExplosion0{}.png".format(i))
	explosion_image = pygame.image.load(explosion_dir).convert_alpha()
	explosion_animation.append(explosion_image)
player = Player()
bullets = pygame.sprite.Group()
missiles = pygame.sprite.Group()
enemys = pygame.sprite.Group()
explosions = pygame.sprite.Group()
powerups = pygame.sprite.Group()

for _ in range(5):
	enemy = Enemy()
	enemys.add(enemy)
game_over = False
pygame.mixer.music.play(loops = -1)


while not game_over:
	framerate.tick(60)
	if game_state == 0:
		show_menu(game_state)
	elif game_state == 2:
		show_menu(game_state)
	else:
		now = pygame.time.get_ticks()
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					player.shoot()
		keys = pygame.key.get_pressed()
		if keys[K_ESCAPE]:
			sys.exit()
		
		hits = pygame.sprite.groupcollide(enemys, bullets, True, True)
		for hit in hits:
			explosion = Explosion(hit.rect.center)
			explosions.add(explosion)
			enemy = Enemy()
			enemys.add(enemy)
			player.add_score(80 - hit.radius)
			if random.random() > 0.9:
				powerup = Powerup(hit.rect.center)
				powerups.add(powerup)

		hits = pygame.sprite.groupcollide(enemys, missiles, True, True)
		for hit in hits:
			explosion = Explosion(hit.rect.center)
			explosions.add(explosion)
			enemy = Enemy()
			enemys.add(enemy)
			player.add_score((80 - hit.radius)*2)
			if random.random() > 0.9: 
				powerup = Powerup(hit.rect.center)
				powerups.add(powerup)

		hits = pygame.sprite.spritecollide(player, enemys, True, pygame.sprite.collide_rect_ratio(0.7))
		for hit in hits:
			explosion = Explosion(hit.rect.center)
			explosions.add(explosion)
			enemy = Enemy()
			enemys.add(enemy)
			player.be_hit(hit.radius)
		hits = pygame.sprite.spritecollide(player, powerups, True)
		for hit in hits:
			if hit.type == 'add_hp':
				player.hp += 50
				if player.hp > 100:
					player.hp = 100
			elif hit.type == 'add_life':
				player.lifes += 1
				if player.lifes > 3:
					player.lifes = 3
					player.hp = 100
			elif hit.type == 'add_missile':
				player.fire_missile()
		
		screen.blit(background_img, background_rect)
		screen.blit(player.image, player.rect)
		player.update()
		bullets.update()
		missiles.update()
		enemys.update()
		explosions.update()
		powerups.update()
		bullets.draw(screen)
		missiles.draw(screen)
		enemys.draw(screen)
		explosions.draw(screen)
		powerups.draw(screen)
		draw_ui()

		pygame.display.update()