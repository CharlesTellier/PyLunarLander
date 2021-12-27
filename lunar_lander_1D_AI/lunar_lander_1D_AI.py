"""
!/usr/bin/env python
#-*- coding: utf-8 -*-

Author: Charles TELLIER
"""

import pygame
import os
from random import randint
import neat

pygame.font.init()

WIN_WIDTH = 1200 # Main window width
WIN_HEIGHT = 800 # Main window height
MOON_FLOOR = 700 # Position of the lunar surface
FRAMERATE = 30 # Number of frame per second
MOON_ACC = 0.3 # Moon's acceleration [m/s²]
BURN_RATE = 150 # [kg/s] Rate of fuel burnt per second
THRUST = 50 # [N] Lunar Lander thrust force
FUEL_MASS = 3000 # [kg] Original fuel mass
MAX_VEL_LANDING = 30 # [m/s] Max landing velocity

LANDER_IMGS = [pygame.image.load(os.path.join("imgs", "lander.jpg")),
			 pygame.image.load(os.path.join("imgs", "lander_burn.jpg"))]

STAT_FONT = pygame.font.SysFont("comicsans", 20)

class MoonLander:
	def __init__(self, y):
		self.x = randint(LANDER_IMGS[0].get_height(), WIN_WIDTH //2 - LANDER_IMGS[0].get_height())
		self.y = y # Vertical position of the lander
		self.tick_count = 0 # To save the number of frame since the last status' changement (burn or falling) for acceleration management
		self.delta_t = 1.0 / FRAMERATE # Time discretisation of the simulation
		self.vel = 0 # Velocity of the lunar lander [m/s]
		self.img = LANDER_IMGS[0] # Displayed image of the lunar lander
		self.static_mass = 2000 # [kg] Mass of the empty lunar module
		self.fuel_mass = FUEL_MASS # [kg] Mass of fuel in the lunar module
		self.mass = self.static_mass + self.fuel_mass # Total mass of the lunar module
		self.burn = False # If True, the rocket engines are activated, if False, the lunar modele is falling
		self.landed = False # If True, the lander can't move, if False, it can

	def move(self):
		if self.landed is False:
			if self.burn:
				fuel_mass_dt = self.fuel_mass - BURN_RATE * self.delta_t # fuel mass burnt during delta_t
				avg_mass = self.static_mass + ((self.fuel_mass + fuel_mass_dt) / 2) # Average mass of the lunar module between t and t+dt
				vel_dt = self.vel + self.tick_count * self.delta_t * ((THRUST / avg_mass) - MOON_ACC) # Average velocity of the lunar module between t and t+dt
				self.fuel_mass = fuel_mass_dt # Updating fuel mass a t+dt
				self.mass = self.static_mass + self.fuel_mass # Updating lunar lander mass at t+dt
			else:
				# Falling
				vel_dt = self.vel + MOON_ACC * self.tick_count * self.delta_t # Lunar lander falling velocity
			self.y = self.y + (self.delta_t / 2) * (self.vel + vel_dt) # New position of the lunar lander
			self.tick_count += 1 # Updating frame count
			self.vel = vel_dt # Updating velocity
		else:
			self.y = MOON_FLOOR - self.img.get_height()
			self.vel = 0

	def draw(self, win, i):
		if self.burn:
			self.img = LANDER_IMGS[1]
		else:
			self.img = LANDER_IMGS[0]
		BLACK = (0, 0, 0)
		self.img.set_colorkey(BLACK)
		if self.vel > MAX_VEL_LANDING:
			velocity = STAT_FONT.render(str(round(abs(self.vel), 2)), 1, (255, 0, 0))
		else:
			velocity = STAT_FONT.render(str(round(abs(self.vel), 2)), 1, (255, 255, 255))
		fuel_pct = STAT_FONT.render(str(round(100 * self.fuel_mass / FUEL_MASS, 2)) + " %", 1, (255, 255, 255))
		altitude = STAT_FONT.render(str(round(MOON_FLOOR - self.y - 50, 0)), 1, (255, 255, 255))
		lander_number = STAT_FONT.render(str(i), 1, (255, 255, 255))
		win.blit(lander_number, (WIN_WIDTH // 2 + 10, 20 + 14 * i))
		win.blit(velocity, (WIN_WIDTH // 2 + 180, 20 + 14 * i))
		win.blit(fuel_pct, (WIN_WIDTH // 2 + 350, 20 + 14 * i))
		win.blit(altitude, (WIN_WIDTH // 2 + 450, 20 + 14 * i))
		win.blit(self.img, (self.x, self.y))

def draw_window(win, moon_landers):
	# Drawing moon floor
	win.fill((0, 0, 0))
	for i, moon_lander in enumerate(moon_landers):
		moon_lander.draw(win, i)
	pygame.draw.line(win, (255, 255, 255), (0, MOON_FLOOR), (WIN_WIDTH // 2, MOON_FLOOR))
	pygame.draw.line(win, (255, 255, 255), (WIN_WIDTH // 2, 0), (WIN_WIDTH // 2 , WIN_HEIGHT))
	lander_banner = STAT_FONT.render("# Moon Lander", 1, (255, 255, 255))
	velocity_banner = STAT_FONT.render("Velocity [m/s]", 1, (255, 255, 255))
	fuel_banner = STAT_FONT.render("Fuel", 1, (255, 255, 255))
	altitude_banner = STAT_FONT.render("Altitude [m]", 1, (255, 255, 255))
	win.blit(lander_banner, (WIN_WIDTH // 2 + 10, 5))
	win.blit(velocity_banner, (WIN_WIDTH // 2 + 180, 5))
	win.blit(fuel_banner, (WIN_WIDTH // 2 + 350, 5))
	win.blit(altitude_banner, (WIN_WIDTH // 2 + 450, 5))

	for i, moon_lander in enumerate(moon_landers):
		if moon_lander.landed:
			landed_banner = STAT_FONT.render("THE EAGLE HAS LANDED !", 1, (255, 255, 255))
			win.blit(landed_banner, (WIN_WIDTH // 4 - landed_banner.get_width() // 2, MOON_FLOOR + 20))
	pygame.display.update()

def main(genomes, config):
	nets = []
	ge = []
	landers=[]

	win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
	clock = pygame.time.Clock()

	for _, g in genomes:
		net = neat.nn.FeedForwardNetwork.create(g, config)
		nets.append(net)
		landers.append(MoonLander(50))
		g.fitness = 0
		ge.append(g)

	run = True
	while run:
		clock.tick(FRAMERATE)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
				quit()
				break

		if len(landers) == 0:
			run = False
			break

		for x, lander in enumerate(landers):
			output = nets[x].activate((MOON_FLOOR - lander.y, lander.vel))
			if output[0] > 0.5:
				lander.burn = True

		for x, lander in enumerate(landers):
			if lander.y >= MOON_FLOOR - lander.img.get_height():
				ge[x].fitness -= abs(lander.vel)
				if lander.vel >= MAX_VEL_LANDING:
					landers.pop(x)
					nets.pop(x)
					ge.pop(x)
				else:
					lander.landed = True
					ge[x].fitness = 200
			elif lander.y <= 0:
				ge[x].fitness += -100000
				landers.pop(x)
				nets.pop(x)
				ge.pop(x)
			else:
				if lander.vel < 0:
					ge[x].fitness += -100000
				else:
					if lander.vel > MAX_VEL_LANDING:
						ge[x].fitness += - lander.vel / 500
					else:
						ge[x].fitness += lander.vel / 30
				if lander.fuel_mass <= 0:
					lander.burn = False

			lander.move()

		draw_window(win, landers)

def run(config_path):
	config = neat.config.Config(neat.DefaultGenome,
								neat.DefaultReproduction,
								neat.DefaultSpeciesSet,
								neat.DefaultStagnation,
								config_path)
	p = neat.Population(config)
	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)

	winner = p.run(main, 20)

if __name__ == "__main__":
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, "config-feedforward")
	run(config_path)
