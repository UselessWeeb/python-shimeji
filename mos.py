import tkinter as tk
from PIL import Image, ImageTk
import random
import pyautogui
import time
import math
import subprocess
from tkinter import PhotoImage

class Shimeji:
    working = False
    dragging = False
    falling = False
    jumping = False
    chasing = False
    def __init__(self, canvas):
        self.canvas = canvas
        self.images_walk_left = [ImageTk.PhotoImage(Image.open(f"walk{i}.png")) for i in range(1, 9)]
        self.images_walk_right = [ImageTk.PhotoImage(Image.open(f"walk{i}.png").transpose(Image.FLIP_LEFT_RIGHT)) for i in range(1, 9)]
        self.images_idle_left = [ImageTk.PhotoImage(Image.open(f"idle{i}.png")) for i in range(1, 21)]
        self.images_idle_right = [ImageTk.PhotoImage(Image.open(f"idle{i}.png").transpose(Image.FLIP_LEFT_RIGHT)) for i in range(1, 21)]
        self.images_fall_left = [ImageTk.PhotoImage(Image.open(f"deploy{i}.png")) for i in range(1, 2)]
        self.images_fall_right = [ImageTk.PhotoImage(Image.open(f"deploy{i}.png").transpose(Image.FLIP_LEFT_RIGHT)) for i in range(1, 2)]
        #landing
        self.images_landing_left = [ImageTk.PhotoImage(Image.open(f"deploy{i}.png")) for i in range(3, 9)]
        self.images_landing_right = [ImageTk.PhotoImage(Image.open(f"deploy{i}.png").transpose(Image.FLIP_LEFT_RIGHT)) for i in range(3, 9)]
        self.image_attack_right = [ImageTk.PhotoImage(Image.open(f"mos_attack_left{i}.png").transpose(Image.FLIP_LEFT_RIGHT)) for i in range(1, 32)]
        self.image_attack_left = [ImageTk.PhotoImage(Image.open(f"mos_attack_left{i}.png")) for i in range(1, 32)]
        self.images_sit_left = [ImageTk.PhotoImage(Image.open(f"sit{i}.png")) for i in range(1, 18)]
        self.images_sit_right = [ImageTk.PhotoImage(Image.open(f"sit{i}.png").transpose(Image.FLIP_LEFT_RIGHT)) for i in range(1, 18)]
        self.images_sleep_left = [ImageTk.PhotoImage(Image.open(f"sleep{i}.png")) for i in range(1, 19)]
        self.images_sleep_right = [ImageTk.PhotoImage(Image.open(f"sleep{i}.png").transpose(Image.FLIP_LEFT_RIGHT)) for i in range(1, 19)]
        self.images_jump_left = [ImageTk.PhotoImage(Image.open(f"jump.png"))]
        self.images_jump_right = [ImageTk.PhotoImage(Image.open(f"jump.png").transpose(Image.FLIP_LEFT_RIGHT))]
        self.images_left_drag_left = [ImageTk.PhotoImage(Image.open(f"pinch_l{i}.png")) for i in range(1, 4)]
        self.images_left_drag_right = [ImageTk.PhotoImage(Image.open(f"pinch_r{i}.png")) for i in range(1, 4)]
        self.images_right_drag_right = [ImageTk.PhotoImage(Image.open(f"pinch_r{i}.png").transpose(Image.FLIP_LEFT_RIGHT)) for i in range(1, 4)]
        self.images_right_drag_left = [ImageTk.PhotoImage(Image.open(f"pinch_l{i}.png").transpose(Image.FLIP_LEFT_RIGHT)) for i in range(1, 4)]
        self.images_mail_left = [ImageTk.PhotoImage(Image.open(f"mail{i}.png")) for i in range(1, 20)]
        self.images_mail_right = [ImageTk.PhotoImage(Image.open(f"mail{i}.png").transpose(Image.FLIP_LEFT_RIGHT)) for i in range(1, 20)]
        self.current_image = None
        self.x = 10
        self.y = canvas.winfo_screenheight() - 400
        self.ground = canvas.winfo_screenheight() - 100
        self.width = canvas.winfo_screenwidth()
        self.is_walking = False
        self.direction = "right"  # Initial direction is left
        self.walk_index = 0
        self.idle_index = 0
        self.fall_index = 0
        self.jump_index = 0
        self.throw_index = 0    
        self.gravity = 1
        self.fall_distance = 0
        self.attack_index = 0
        self.attack_chance = 5;
        self.rest = 0
        self.jumping = False
        self.set_new_target()
        self.dragging = False
        self.max_speed = 20  # Adjust this value to change the maximum speed of the Shimeji
        self.falling = False
        self.mail = None

    def mail_throwing(self):
        # Delete the old image
        if self.current_image is not None:
            self.canvas.delete(self.current_image)

        # Create a new image
        if self.direction == "left":
            self.current_image = self.canvas.create_image(self.x, self.y, image=self.images_mail_left[self.throw_index])
        else:
            self.current_image = self.canvas.create_image(self.x, self.y, image=self.images_mail_right[self.throw_index])

        self.throw_index = (self.throw_index + 1) % len(self.images_mail_left)

        if self.throw_index  == 6:
            #create mail here
            if self.mail is not None:
                del self.mail
            if self.direction == "left":
                self.mail = Mail(self.canvas, self.x-20, self.y-10, -2, 0, self.y)
            else:
                self.mail = Mail(self.canvas, self.x+20, self.y-10, 2, 0, self.y)
            self.mail.throw()
        if self.throw_index < 18:
            self.canvas.after(100, self.mail_throwing)
        else:
            self.working = False
            self.throw_index = 0          
            self.idle()

    def landing(self):
        # Play the fall animation here
        if self.current_image is not None:
            self.canvas.delete(self.current_image)
        # Create a new image
        if self.direction == "left":
            self.current_image = self.canvas.create_image(self.x, self.y, image=self.images_landing_left[self.fall_index])
        else:
            self.current_image = self.canvas.create_image(self.x, self.y, image=self.images_landing_right[self.fall_index])
        self.fall_index = (self.fall_index + 1) % len(self.images_landing_left)
        if self.fall_index < 5:
            self.canvas.after(100, self.landing)
        if self.fall_index == 5:
            self.fall_index = 0
            self.falling = False
            self.idle();
    
    def start_drag(self, event):
        self.dragging = True
        self.is_climbing = False
        # attack the mouse
        if (random.randint(0, 2) == 1):
            self.play_attack_animation()
        else:
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self.drag_start_time = time.time()
            self.total_dx = 0  # Total distance moved in x direction
            self.total_dy = 0  # Total distance moved in y direction
            # Calculate the angle between the mouse and the Shimeji

    def drag(self, event):
        if self.dragging:
            dx = event.x - self.x
            dy = event.y - self.y
            self.total_dx += dx
            self.total_dy += dy
            self.canvas.move(self.current_image, dx, dy)
            self.x += dx
            self.y += dy

            # Calculate the speed as the distance moved since the last frame
            speed = math.sqrt(dx**2 + dy**2)
            # Map the speed to the range -90 to 90 for the angle
            # Adjust the constants as necessary to get the desired behavior
            angle = (speed/5) * 180 / math.pi
            if dx < 0:
                angle = -angle

            angle = max(-90, min(90, angle))

            if dx != 0 or dy != 0:
                self.angle = angle
            else:
            # If the mouse is not moving, decay the angle towards zero
                self.angle *= 0.9  # adjust this value to change the speed of the decay
            if self.direction == "left":
                if angle < -45 and angle >= -90:
                    new_image = self.images_left_drag_right[2]
                elif angle < -10 and angle >= -45:
                    new_image = self.images_left_drag_right[1]
                elif angle >= -10 and angle < 0:
                    new_image = self.images_left_drag_right[0]
                elif angle >= 0 and angle < 10:
                    new_image = self.images_left_drag_left[0]
                elif angle >= 10 and angle < 45:
                    new_image = self.images_left_drag_left[1]
                elif angle >= 45 and angle <= 90:
                    new_image = self.images_left_drag_left[2]
            else:
                if angle < -45 and angle >= -90:
                    new_image = self.images_right_drag_left[2]
                elif angle < -10 and angle >= -45:
                    new_image = self.images_right_drag_left[1]
                elif angle >= -10 and angle < 0:
                    new_image = self.imagesv_drag_left[0]
                elif angle >= 0 and angle < 10:
                    new_image = self.images_right_drag_right[0]
                elif angle >= 10 and angle < 45:
                    new_image = self.images_right_drag_right[1]
                elif angle >= 45 and angle <= 90:
                    new_image = self.images_right_drag_right[2]

            # If the current image doesn't exist, create it
            if self.current_image is None:
                self.current_image = self.canvas.create_image(self.x, self.y, image=new_image)
            else:
                # Otherwise, just update the image property of the current image
                self.canvas.itemconfig(self.current_image, image=new_image)
        

    def stop_drag(self, event):
        self.falling = True

        # Set the target position to the current position
        self.target_x = self.x
        self.target_y = self.y

        # Calculate the final mouse speed
        dt = max(time.time() - self.drag_start_time, 1e-6)  # prevent division by zero
        self.speed_x = self.total_dx / dt
        self.speed_y = self.total_dy / dt

        # Clamp the speed to the maximum speed
        speed = math.sqrt(self.speed_x**2 + self.speed_y**2)
        if speed > self.max_speed:
            self.speed_x = self.speed_x / speed * self.max_speed
            self.speed_y = self.speed_y / speed * self.max_speed

        self.move_towards_target()  # Start moving towards the target

    def move_towards_target(self):
        # Calculate the distance to the target
        dx = self.target_x - self.x
        dy = self.target_y - self.y

        # Calculate the step to move in this frame
        step_x = min(abs(dx), 1) * (1 if dx > 0 else -1)
        step_y = min(abs(dy), 1) * (1 if dy > 0 else -1)

        # Move the sprite
        self.canvas.move(self.current_image, step_x, step_y)
        self.x += step_x
        self.y += step_y

        # Check if the sprite has reached the target
        if abs(self.target_x - self.x) > 1 or abs(self.target_y - self.y) > 1:
            # If not, continue moving in the next frame
            self.canvas.after(10, self.move_towards_target)
        #but if it touch the wall, climb
        else:
            # If yes, start the fall animation
            self.fall()
        
    def fall(self):
        # Check if the sprite is already on the ground
        if self.y >= self.ground:
            self.dragging = False
            self.falling = False
            self.idle();
            self.x = round(self.x)  
            self.y = round(self.y)  
            return  # Return immediately without doing anything

        # Play the fall animation here
        if self.current_image is not None:
            self.canvas.delete(self.current_image)
        # Create a new image
        if self.speed_x < 0:
            self.current_image = self.canvas.create_image(self.x, self.y, image=self.images_fall_left[self.fall_index])
        else:
            self.current_image = self.canvas.create_image(self.x, self.y, image=self.images_fall_right[self.fall_index])
        self.fall_index = (self.fall_index + 1) % len(self.images_fall_left)

        # Update the Shimeji's position based on the speed
        self.x += self.speed_x
        self.y += self.speed_y

        # Update the y-speed based on gravity
        self.speed_y += self.gravity

        # Check if the Shimeji has hit the ground or the screen boundaries
        if self.y >= self.ground:        
            self.x = round(self.x)
            self.y = self.ground  # reset the position to the ground level
            self.dragging = False
            self.landing()
        elif self.x <= 0 or self.x >= self.width:           
            self.dragging = False
            self.x = 900
            self.y = 0
            self.fall();
        else:
            self.canvas.after(10, self.fall)  # Continue the fall animation
    
    def play_attack_animation(self):
        # Delete the old image
        if self.current_image is not None:
            self.canvas.delete(self.current_image)

        # Create a new image
        if self.direction == "left":
            self.current_image = self.canvas.create_image(self.x, self.y, image=self.image_attack_left[self.attack_index])
        else:
            self.current_image = self.canvas.create_image(self.x, self.y, image=self.image_attack_right[self.attack_index])

        self.attack_index = (self.attack_index + 1) % len(self.image_attack_left)

        if self.attack_index < 30:
            self.canvas.after(25, self.play_attack_animation)
        else:
            self.dragging = False
            self.idle()
            self.freeze_mouse(2, self.x, self.y)
            self.attack_index = 0
            
    def freeze_mouse(self, time_sec, maxX, maxY):
        if time_sec > 0:
            time_sec -= 0.1
            pyautogui.moveTo(maxX, maxY)
            self.canvas.after(10, lambda: self.freeze_mouse(time_sec, maxX, maxY))  # Schedule the next call

    def walk(self):
        if not self.is_walking:
            self.is_walking = True
            self.walk_animation()
            
    def special_jump(self):
        # it's still a jump, so I call jump
        self.jump()

        # Schedule the mouse movement and click to happen after the jump is finished
        self.canvas.after(self.falling == False, self.perform_mouse_actions)

    def perform_mouse_actions(self):
        mouse_x, mouse_y = pyautogui.position()

        # Move the mouse to the target location and click
        pyautogui.moveTo(self.target_x, self.target_y)
        pyautogui.click()

        # Move the mouse back to the original location
        pyautogui.moveTo(mouse_x, mouse_y)

    
    def jump(self):
        self.gravity = 1
        distance_x = self.target_x - self.x
        distance_y = self.target_y - self.y

        # Calculate the time it would take to reach the target x-coordinate at a constant speed
        speed_x = 10  # Adjust this value to change the speed of the jump
        time = abs(distance_x / speed_x)

        # Calculate the initial y-velocity needed to reach the target y-coordinate in the same time
        self.velocity_y = (distance_y - 0.5 * self.gravity * time**2) / time
        self.velocity_x = speed_x if self.target_x > self.x else -speed_x
          # Adjust this value to change the gravity of the jump

        self.jumping = True

        # Start the jump
        self.jump_animation()

    def jump_animation(self):
        # Apply the velocity to the position
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Apply gravity to the y velocity
        self.velocity_y += self.gravity

        # Play the jump animation here
        if self.current_image is not None:
            self.canvas.delete(self.current_image)
        # Create a new image
        if self.direction == "left":
            self.current_image = self.canvas.create_image(self.x, self.y, image=self.images_jump_left[0])
        else:
            self.current_image = self.canvas.create_image(self.x, self.y, image=self.images_jump_right[0])

        if (self.velocity_x > 0 and self.x < self.target_x) or (self.velocity_x < 0 and self.x > self.target_x):  # If the Shimeji hasn't reached the target yet
            self.canvas.after(10, self.jump_animation)  # Continue the jump animation
        else:  # If the Shimeji has reached the target
            self.velocity_x = 0  # Reset the x velocity
            self.velocity_y = 0  # Reset the y velocity
            self.jumping = False
            self.is_walking = False
            #round self y
            self.x = round(self.x)
            self.y = round(self.y)

            self.landing()  # Land and go back to idle
               
    def set_new_target(self):
        if self.dragging or self.is_walking or self.falling or self.jumping:
            return
        rand = random.randint(0, 25)
        if rand == 1:
            self.chasing = True
            self.chase_mouse()
        elif rand > 1 and rand <= 5:
            self.working = True
            self.mail_throwing()
        else:
            self.target_x = random.randint(0, 1800)
            self.target_y = random.randint(0, 900)  
            self.direction = "left" if self.target_x < self.x else "right"  
            self.is_walking = True
            movement = random.randint(0, 1)
            if (movement == 1 ): 
                self.walk_animation()
            elif (movement == 0):
                if (random.randint(0, 1) == 1):
                    self.jump()
                else:
                    
                    self.special_jump()

    def chase_mouse(self):
        if self.is_walking or self.chasing:
            return
        self.is_walking = True
        self.chasing = True  
        self.target_x, self.target_y = pyautogui.position()
        self.walk_animation()

    def walk_animation(self): 
        if self.dragging or self.falling or self.jumping:
            self.is_walking = False
            return       
        # Delete the old image
        if self.current_image is not None:
            self.canvas.delete(self.current_image)

        if self.chasing:
            self.target_x, self.target_y = pyautogui.position()

        # Update the direction based on the current and target x-coordinates
        if self.x != self.target_x:
            if self.target_x < self.x: 
                self.direction = "left"  
            elif self.target_x > self.x:
                self.direction = "right"
            else:
                self.direction = self.direction

        # Create a new image
        if self.direction == "left":
            self.current_image = self.canvas.create_image(self.x, self.y, image=self.images_walk_left[self.walk_index])
        else:
            self.current_image = self.canvas.create_image(self.x, self.y, image=self.images_walk_right[self.walk_index])

        self.canvas.tag_bind(self.current_image, '<Button-1>', self.start_drag)
        self.canvas.tag_bind(self.current_image, '<B1-Motion>', self.drag)
        self.canvas.tag_bind(self.current_image, '<ButtonRelease-1>', self.stop_drag)

        self.walk_index = (self.walk_index + 1) % len(self.images_walk_left)

        if self.direction == "left" and self.x > self.target_x:
            self.x -= 1
        elif self.direction == "right" and self.x < self.target_x:
            self.x += 1

        if self.y < self.target_y:
            self.y += 1
        elif self.y > self.target_y:
            self.y -= 1
            
        if self.dragging or (self.x == round(self.target_x) and self.y == round(self.target_y)):
            self.is_walking = False
            if self.chasing:
                self.chasing = False
                self.play_attack_animation()
            else:
                self.idle()
        else:
            self.canvas.after(100, self.walk_animation)

    def start_rest(self):
        # Create a rest action
        if not hasattr(self, 'rest_action'):
            self.rest_action = random.randint(0, 2)
        
        self.idle_index = 0

    # Start the rest period
        self.canvas.after(random.randint(5000, 15000), self.end_rest)

    def end_rest(self):
    # End the rest period
        if hasattr(self, 'rest_action'):
            del self.rest_action
            self.rest = 0

    # Set a new target
        self.set_new_target()

    def idle(self):
        if self.dragging or self.is_walking or self.falling or self.jumping or self.working:
            return  
        self.is_walking = False
        self.falling = False
        self.jumping = False
        self.dragging = False
        # Delete the old image
        if self.current_image is not None and self.canvas.find_withtag(self.current_image):
            self.canvas.delete(self.current_image)
        
        #start res here
        if not self.dragging and not self.is_walking and self.rest == 0:
            self.start_rest()
            self.rest = 1

        if self.rest_action == 0:
            if self.direction == "left":
                self.current_image = self.canvas.create_image(self.x, self.y, image=self.images_sit_left[self.idle_index])
            else:
                 self.current_image = self.canvas.create_image(self.x, self.y, image=self.images_sit_right[self.idle_index])

            self.idle_index = (self.idle_index + 1) % len(self.images_sit_left)
        elif self.rest_action == 1:
            if self.direction == "left":
                self.current_image = self.canvas.create_image(self.x, self.y, image=self.images_sleep_left[self.idle_index])
            else:
                self.current_image = self.canvas.create_image(self.x, self.y, image=self.images_sleep_right[self.idle_index])
                
            self.idle_index = (self.idle_index + 1) % len(self.images_sleep_left)
        else:
            if self.direction == "left":
                self.current_image = self.canvas.create_image(self.x, self.y, image=self.images_idle_left[self.idle_index])
            else:
                self.current_image = self.canvas.create_image(self.x, self.y, image=self.images_idle_right[self.idle_index])

            self.idle_index = (self.idle_index + 1) % len(self.images_idle_left)
        
        if self.current_image is not None and self.canvas.find_withtag(self.current_image):
            self.canvas.tag_bind(self.current_image, '<Button-1>', self.start_drag)
            self.canvas.tag_bind(self.current_image, '<B1-Motion>', self.drag)
            self.canvas.tag_bind(self.current_image, '<ButtonRelease-1>', self.stop_drag)

        # Call the idle method again after a delay to create the animation
        if not self.is_walking or self.dragging:
            self.canvas.after(100, self.idle)

class Mail:
    def __init__(self, canvas, x, y, vx, vy, ground):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.ground = ground
        self.image = PhotoImage(file="mail_img.png")  # Add your image here
        self.mail_image = self.canvas.create_image(self.x, self.y, image=self.image)   
        # Bind the click event to the click method
        self.canvas.tag_bind(self.mail_image, '<Button-1>', self.click)
        self.destroy_timer = canvas.after(7000, self.destroy)

    def throw(self):
        # Update position
        self.x += self.vx
        self.y += self.vy

        # Apply gravity
        self.vy += 0.3

        # Stop falling when it reaches the same y as Shimeji
        if self.y >= self.ground+50:  # Replace 900 with the actual y position of Shimeji
            self.vy = 0
            self.vx = 0

        # Move the image to the new position
        self.canvas.move(self.mail_image, self.vx, self.vy)

        # Call the update method again after a delay to create the animation
        self.canvas.after(50, self.throw)

    def click(self, event):  
        self.canvas.after_cancel(self.destroy_timer)
        with open('your_file.txt', 'w') as f:
            f.write('Dear Doctor,')
            if random.randint(0, 5) == 1:
                f.write("You know, I've always had my doubts about Emperor saying you're a member of Penguin Logistics. You're too nice and your attitude doesn't fit our image... But hey, seeing Rhodes Island as it's own now, I found that you're actually a pretty interesting one. I'm glad to have you as a friend.")
            elif random.randint(0, 5) == 2:
                f.write("I know you're trying to get closer to me, but I'm not interested in that kind of relationship. I'm not interested in any kind of relationship, really. I'm not interested in you, either. I'm not interested in anything. I'm just... not interested. I'm sure you'll find someone else, so don't worry about me.")
            elif random.randint(0, 5) == 3:
                f.write("You don't need to concern yourself with how to have a good relationship with me. For me, friends, family, and love... I have nothing against them, but I don't need them either. Heh, not like that's going to stop you from trying, right? Well, I don't really mind, so give it your best shot")
            elif random.randint(0, 5) == 4:
                f.write("I'm not a fan of the cold, but I do like the snow. It's so pure, so clean, so... beautiful. It's like a white canvas, waiting for someone to paint on it. I wonder what kind of painting you'd make, Doctor.")
            else:
                f.write("I don't know why you're so interested in me, but I'm not going to stop you. I'll be watching you, Doctor. Don't disappoint me.")
            f.write('\n\n')
            f.write('Sincerely,')
            f.write('\n')
            f.write('Mostima')
        try:
            subprocess.run(['notepad.exe', 'your_file.txt'])
        except Exception as e:
            print(f"Error when trying to open Notepad: {e}")
        self.canvas.delete(self.mail_image)
        del self

    def destroy(self):
        self.canvas.delete(self.mail_image)
        del self
            
def main():
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.overrideredirect(True)  # Remove window decorations
    canvas = tk.Canvas(root, bg="#0f0f0f", highlightthickness=0)  # Set the background color to white
    root.wm_attributes("-topmost", True)  # Make the window stay on top
    root.attributes("-transparentcolor", "#0f0f0f")  # Make white color transparent
   
    canvas.pack(fill=tk.BOTH, expand=True)

    shimeji = Shimeji(canvas)
    

    root.mainloop()

if __name__ == "__main__":
    main()