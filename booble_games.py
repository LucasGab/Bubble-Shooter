import pygame
import math
import random
from pygame.locals import *

#Variáveis Globais
colors_name = ['white','red','green','blue'] # Possíveis cores das bolas
colors = { 'black':(0,0,0), 'white':(255,255,255), 'red':(255,0,0), 'green':(0,255,0), 'blue':(0,0,255) } # Cores do jogo
screen_width = 640 # Tamanho da tela em x
screen_height = 480 # Tamanho da tela em y
BALL_RADIUS = 20 # Raio da bola
WIDTH_LINE = 2  # Largura da linha
SIZE_LINE = 250 # Tamanha da linha
BULLET_RATE = 300 # Frequencia de tiro


# Globais do pygame
pygame.init()
window = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Bubble Shooter") 
#pygame.display.set_icon() #escolhe o icone do jogo
pygame.mouse.set_visible(False) #Oculta o mouse 

# Objeto bola
class Ball: 
    def __init__ (self, pos_x, pos_y,cor): #Inicia as variáveis da bola 
        self.x = pos_x
        self.y = pos_y
        self.vel_x = 0
        self.vel_y = 0
        self.color = cor 
    def Draw(self): #Desenha a bola
        pygame.draw.circle(window,self.color,[int(self.x),int(self.y)],BALL_RADIUS)
    def Walk(self): 
        # Metodo que faz a bola se mover
        self.x += self.vel_x
        self.y += self.vel_y
    def Shoot(self, vel_x, vel_y): 
        # Metodo que atira a bola
        self.vel_x = vel_x
        self.vel_y = vel_y
    def Collide_Wall(self):
        # Metodo que verifica se a bola bate na parede
        if(self.x < BALL_RADIUS or self.x > screen_width-BALL_RADIUS): # se bateu nas paredes laterais rebate
            self.vel_x *= -1
        if(self.y > screen_height-BALL_RADIUS): # se bateu na parede de baixo rebate
            self.vel_y *= -1
        if(self.y < BALL_RADIUS): # se bateu na parede de cima mantém ela lá
            self.vel_x = 0
            self.vel_y = 0
    def Collide(self,ball_game):
        # Metodo que retorna se duas bolas colidiram
        if(math.sqrt( ((self.x - ball_game.x)**2 ) + ( (self.y - ball_game.y)**2 )) <= (2*BALL_RADIUS)):
            self.x = int(self.x)
            self.y = int(self.y)
            return True
        else:
            return False
    def Explode(self,balls_game,position,cont):
        #Metodo recursivo que elimina as bolas de mesmas cores que estão em contato

        ball = balls_game[position]
        balls_game.pop(position)
        cont += 1
        i = 0
        tam = len(balls_game)
        while(i < tam):
            if balls_game[i] != ball  and balls_game[i].Collide(ball) and (balls_game[i].color == ball.color):
                cont += balls_game[i].Explode(balls_game,i,cont)
                tam -= cont
                i -= cont
            i += 1
            
        return cont

#Funções do jogo
def get_Ball(x,y,cor):
    #Retorna as bolas de acordo com o parâmetro
    return Ball(x,y,colors[cor])
def Boot_Bullet():
    #Retorna as bolas que serão atiradas, com cor aleatória
    return Ball((int)(screen_width/2),screen_height-BALL_RADIUS,colors[random.choice(colors_name)])
def Open_File(): 
    # Le um arquivo com o numero de bullets ja jogadas, e o vetor de bolas 
    # Le do "input.txt"
    arq = open('input.txt','r')
    bolas = []
    text = arq.readlines()
    for line in text:
        word = line.split()
        if(len(word) > 1):
            bolas.append(get_Ball(int(word[1]),int(word[2]),word[0]));
    arq.close()
    return bolas

def State_File(total_shoots,balls_game): 
    # Salva uma fase em arquivo
    # Salva no "output.txt"
    arq = open("output.txt",'w')
    text = []
    color_name = ""
    text.append((str(total_shoots)+'\n'))
    for ball in balls_game:
        for name, color in colors.items():
            if color == ball.color:
                color_name = name
        if(ball != balls_game[len(balls_game)-1]):  
            text.append((color_name + ' ' + str(ball.x) + ' ' + str(ball.y) + '\n'))
        else:
            text.append((color_name + ' ' + str(ball.x) + ' ' + str(ball.y)))
    arq.writelines(text)
    arq.close()
def get_angle(x1,y1,x2,y2):
    #Retorna o angulo de dois pontos
    return (y2-y1)/(x2-x1)

def get_vel(x1,y1,x2,y2):
    #Retorna a velocidade da bola de acordo com o angulo
    xd = (x2-x1)
    yd = (y2-y1)
    if(xd != 0):
        Angle = math.degrees(math.atan(yd/xd))
        vel_x = math.cos(math.radians(Angle))
        vel_y = math.sin(math.radians(Angle))
        if(vel_y >= 0):
            vel_y = vel_y*-1
            vel_x = vel_x*-1
    else:
        vel_x = 0
        vel_y = -1

    return [vel_x*4,vel_y*4]
        
def get_point_line(x1,y1,x2,y2):
    #Retorna as coordenadas x e y do ponto final da linha, através do ângulo do mouse
    if(x2-x1 !=0):
        m = (get_angle(x1,y1,x2,y2))
        if(m < 0):
            x = (SIZE_LINE/math.sqrt(((m*m)+1)))+x1
            y = y1 + ((m*(x-x1)))
        else:
            x = -(SIZE_LINE/math.sqrt(((m*m)+1)))+x1
            y = y1 +((m*(x-x1)))
    else:
        x = x1
        y = y1-SIZE_LINE
        
    return [x,y]

# Inicializacao das variaveis do jogo

bullets_game = [Boot_Bullet()]# Vetor de bolas de atirar
balls_game = Open_File() # Vetor das bolas alvos
loop = True
mouse_x = 0
mouse_y = 0

clock = pygame.time.Clock() # Relógio do jogo
last_time = 0 # Ultimo tempo
total_shoots = 0 # Quantidade de jogadas

while loop:
    pygame.display.update()
    for event in pygame.event.get():
        (mouse_x, mouse_y) = pygame.mouse.get_pos() # posicao do mouse 

        if event.type == pygame.QUIT: # fechar janela 
            loop = False 
            break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                State_File(total_shoots,balls_game)
        if pygame.mouse.get_pressed() == (1,0,0): # pressionou o mouse
            if(pygame.time.get_ticks()-last_time > BULLET_RATE): # Se o tempo passado do ultimo tiro for maior que a taxa de tiro, atira a bala
                #Atira a bola que está no canhão e gera uma nova para repor ela
                total_shoots+=1
                bullet = bullets_game[len(bullets_game)-1]
                vel_x,vel_y = get_vel((int)(screen_width/2),screen_height-BALL_RADIUS,mouse_x,mouse_y)
                bullet.Shoot(vel_x,vel_y)
                bullets_game.append(Boot_Bullet())
                last_time = pygame.time.get_ticks()


    #Preenche o fundo com preto e a linha da trajetória do tiro
    window.fill(colors['black'])
    x,y = get_point_line((int)(screen_width/2),screen_height-BALL_RADIUS,mouse_x,mouse_y)
    pygame.draw.line(window,colors['blue'],[(int)(screen_width/2),screen_height-BALL_RADIUS],[int(x),int(y)],WIDTH_LINE) # desenha uma linha da posicao de lancamento ate o mouse 

    # Tamanho dos vetores das balas e das bolas alvo
    tam1 = len(bullets_game)
    tam2 = len(balls_game)
    i = 0
    #Verifica se alguma bala atirada pelo canhão colidiu com as bolas alvos, e chama o método recursivo caso sejam da mesma cor
    while(i < tam1):
        j = 0
        while(j < tam2):
            if(bullets_game[i].Collide(balls_game[j])):
                    bullets_game[i].vel_x = 0
                    bullets_game[i].vel_y = 0
                    if(bullets_game[i].color == balls_game[j].color):
                        cont = bullets_game[i].Explode(balls_game,j,0)
                        j -= cont
                        tam2 -= cont
                    else:
                        balls_game.append(bullets_game[i])
                    bullets_game.pop(i)
                    i -= 1
                    tam1 -= 1
                    
            j+=1
        i =i+1
    for bullet in bullets_game:
        bullet.Collide_Wall() # Verifica se a bola bateu nas paredes
    for bullet in bullets_game:
        bullet.Walk() # Move as balas
    for bullet in bullets_game:        
        bullet.Draw() # Desenha as balas na tela
    for ball in balls_game:
        ball.Draw() # Desenha as bolas alvo na tela


    pygame.display.update() # Atualiza a tela
    clock.tick(60) # Limita os frames a 60 por segundo
    
pygame.quit()# Sai do jogo
