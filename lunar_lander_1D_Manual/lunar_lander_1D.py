"""
!/usr/bin/env python
#-*- coding: utf-8 -*-

Author: Charles TELLIER
"""

import pygame
import os

pygame.font.init()

WIN_WIDTH = 600
WIN_HEIGHT = 800
MOON_FLOOR = 700
FRAMERATE = 30
MOON_ACC = 0.3 # m/s²
BURN_RATE = 150 # [kg/s] Rate of fuel burn per second
THRUST = 50 # [N] Lunar Lander thrust force
FUEL_MASS = 3000 # [kg] Original fuel mass
MAX_VEL_LANDING = 10 # [m/s] Max landing velocity

LANDER_IMGS = [pygame.image.load(os.path.join("imgs", "lander.jpg")),
			 pygame.image.load(os.path.join("imgs", "lander_burn.jpg"))]

STAT_FONT = pygame.font.SysFont("comicsans", 30)

class MoonLander:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.tick_count = 0
		self.delta_t = 1.0 / FRAMERATE
		self.vel = 0
		self.img = LANDER_IMGS[0]
		self.static_mass = 2000 # [kg] Mass of the empty lunar module
		self.fuel_mass = FUEL_MASS # [kg] Mass of fuel in the lunar module
		self.mass = self.static_mass + self.fuel_mass
		self.destroyed = False

	def move(self, burn):
		if burn:
			fuel_mass_dt = self.fuel_mass - BURN_RATE * self.delta_t
			avg_mass = self.static_mass + ((self.fuel_mass + fuel_mass_dt) / 2)
			vel_dt = self.vel + self.tick_count * self.delta_t * ((THRUST / avg_mass) - MOON_ACC)

			self.fuel_mass = fuel_mass_dt
			self.mass = self.static_mass + self.fuel_mass
		else:
			# Falling
			vel_dt = self.vel + MOON_ACC * self.tick_count * self.delta_t

		self.y = self.y + (self.delta_t / 2) * (self.vel + vel_dt)
		self.tick_count += 1
		self.vel = vel_dt


	def draw(self, win, burn):
		if self.destroyed is False:
			if burn:
				self.img = LANDER_IMGS[1]
			else:
				self.img = LANDER_IMGS[0]

		if self.vel > MAX_VEL_LANDING:
			velocity = STAT_FONT.render("Velocity: " + str(round(abs(self.vel), 2)) + " m/s", 1, (255, 0, 0))
		else:
			velocity = STAT_FONT.render("Velocity: " + str(round(abs(self.vel), 2)) + " m/s", 1, (255, 255, 255))
		fuel_pct = STAT_FONT.render("Fuel: " + str(round(100 * self.fuel_mass / FUEL_MASS, 2)) + " %", 1, (255, 255, 255))
		altitude = STAT_FONT.render("Altitude: " + str(round(MOON_FLOOR - self.y - 50, 0)) + " m", 1, (255, 255, 255))
		win.blit(velocity, (20, MOON_FLOOR + 20))
		win.blit(fuel_pct, (WIN_WIDTH - 20 - fuel_pct.get_width(), MOON_FLOOR + 20))
		win.blit(altitude
			, (20, MOON_FLOOR + 60))
		win.blit(self.img, (self.x, self.y))


def draw_window(win, moon_lander, burn):
	# Drawing moon floor
	win.fill((0, 0, 0))
	moon_lander.draw(win, burn)
	pygame.draw.line(win, (255, 255, 255), (0, MOON_FLOOR), (WIN_WIDTH, MOON_FLOOR))
	pygame.display.update()

def main():
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    moon_lander = MoonLander(WIN_WIDTH // 2 - 50 // 2, 50)
    clock = pygame.time.Clock()

    run = True
    burn = False
    while run:
        clock.tick(FRAMERATE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
            	burn = True
            	moon_lander.tick_count = 0
            if event.type == pygame.KEYUP and event.key == pygame.K_UP:
            	burn = False
            	moon_lander.tick_count = 0

        if moon_lander.y >= MOON_FLOOR - 50:
        	if moon_lander.vel >= MAX_VEL_LANDING:
        		 run = False
        		 break
       		else:
       			moon_lander.y = MOON_FLOOR - 50
       			moon_lander.vel = 0
       	else:
       		if moon_lander.fuel_mass <= 0:
       			burn = False
        	moon_lander.move(burn)

        draw_window(win, moon_lander, burn)

if __name__ == "__main__":
    main()
