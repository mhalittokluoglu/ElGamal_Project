import time
import serial
import math
import tkinter as tk
import random


class ElGamal:
    def __init__(self,win):
        self.ser =  serial.Serial("/dev/ttyS0", baudrate= 9600, parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
        frame1 = tk.Frame(win)
        frame1.grid(row = 0, column = 0)
        sb = tk.Scrollbar(frame1)
        sb.grid(row=1,column=1)
        self.setting_bu = tk.Button(frame1, text = 'Seçenekler', bg='#DDEEFF',command=self.settings_func)
        self.text_t = tk.Text(frame1,height=20,state='disabled',yscrollcommand = sb.set)
        self.send_e=tk.Entry(frame1,width = 80)
        clear_bu = tk.Button(frame1,text='Temizle',command = self.clear_function)
        self.send_bu = tk.Button(frame1,text='Gönder',command = self.send_function)

        self.send_e.bind("<Return>", self.send_function)

        self.setting_bu.grid(row = 0, column = 0, columnspan = 2,sticky='W')
        self.text_t.grid(row = 1, column = 0,rowspan = 2)
        clear_bu.grid(row = 1,column = 1,sticky='N')
        self.send_e.grid(row = 3, column = 0)
        self.send_bu.grid(row = 3, column = 1)
        sb.config( command = self.text_t.yview )

        self.own_nick = 'Pi-1'
        self.own_id = 12345678
        self.ot_id = 87654321
        self.ot_nick = 'Pi-2'
        self.prime=24391
        self.p_root = 3
        self.own_num = 367
        self.own_publ = pow(self.p_root,self.own_num)%self.prime
        
        self.r_message = ''
        self.con_message = ''
        self.r_finished=False
        self.is_connected = False
        self.serseri =  serial.Serial("/dev/ttyS0", baudrate= 9600, parity=serial.PARITY_NONE,
                 stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS,timeout=0.3)
        self.serseri2 = serial.Serial("/dev/ttyS0", baudrate= 9600, parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS,timeout = 1)
        self.update_func()
        

        
    def update_func(self):
        self.receiver()
        if(self.r_finished):
            self.text_t.configure(state='normal')
            self.text_t.insert(tk.END,self.r_message)
            self.text_t.configure(state='disabled')
            self.r_finished = False
            self.r_message = ''
        self.text_t.after(50,self.update_func)
        
    def send_function(self,*args):
        data = self.send_e.get()
        data = data + '\n'
        self.sender(data)
        self.text_t.configure(state='normal')
        self.text_t.insert(tk.END,self.own_nick+': '+data)
        self.send_e.delete(0,'end')
        self.text_t.configure(state='disabled')

    def clear_function(self):
        self.text_t.configure(state='normal')
        self.text_t.delete('1.0','end')
        self.text_t.configure(state='disabled')
        
    def eg_encrypt(self,nmb):
        return (nmb*self.Key)%self.prime
        

    def long_to_byte(self,num):
        a = bytearray()
        a.append(int(num%16))
        for i in range(0,3):
            num = math.floor(num/16)
            if num>=16:
                a.insert(0,int(num%16))
            elif num > 0:
                a.insert(0,int(num))
            else:
                a.insert(0,int(0))
        return a


    def sender(self, data1):
        i = 0
        while True:
            if len(data1)>8+i:
                data2 = data1[i:i+8]
                for e in data2:
                    x = self.eg_encrypt(ord(e))
                    a = self.long_to_byte(x)
                    self.ser.write(a)
                time.sleep(1)
            else:
                data2 = data1[i:]
                for e in data2:
                    x = self.eg_encrypt(ord(e))
                    a = self.long_to_byte(x)
                    self.ser.write(a)
                break
            i+=8

    
                

    def mod_inverse(self,number,mod_number):
        no_inv = False
        list1 = []
        h1 = [mod_number]
        h2 = [number,int(math.floor(mod_number/number))]
        h3 = [mod_number%number]
        while(True):
            list1.append([h1,h2,h3])
            if h3[0] == 1:
                break
            elif h3[0] == 0:
                no_inv = True
                break
            h1 = [h2[0]]
            h2 = [h3[0],int(math.floor(h1[0]/h3[0]))]
            h3 = [h1[0]%h3[0]]
    
        if no_inv:
            print('There is no inverse')
            return 0
    
        list2 = []
        for line in list1:
            for items in line:
                for item in items:
                    list2.append(item)
    
        list2.reverse()
        list3 = []
        i = 3
        for item in list2:
            if i%4 == 0:
                list3.append(item)
            i += 1
    
        prev = 0
        currnt = 1
        for item in list3:
            hold_var = currnt
            currnt = -item*currnt + prev
            prev = hold_var
    
        if currnt < 0:
            currnt = mod_number+currnt
        return currnt

    def eg_decrypte(self,c,Key_inv):
	    return (c*Key_inv)%self.prime

    def byte_to_long(self,a):
        num = 0
        counter = 0
        for i in a:
            if counter < 3:
                num = 16*(num+i)
            else:
                num = num+i
            counter+=1
        return num


    def receiver(self):
        if self.is_connected:
            data_r = self.serseri.read(size = 4)
            c = self.byte_to_long(data_r)
            m = self.eg_decrypte(c,self.Key_inv)
            if m>=20:
                self.r_message = self.r_message + chr(m)
            elif m == 10:
                self.r_message += chr(m)
                self.r_message = self.ot_nick+': '+self.r_message
                self.r_finished=True
        else:
            m = self.serseri2.read()
            m = int.from_bytes(m,"big")
            if m>=20:
                self.con_message = self.con_message + chr(m)
            elif m == 10:
                self.try_to_connect()
                print(self.con_message)

    def try_to_connect(self):
        message = self.con_message.split(',')
        if int(message[0]) == self.own_id:
            self.ot_id = int(message[1])
            self.ot_nick = message[2]
            self.prime = int(message[3])
            self.p_root = int(message[4])
            self.ot_publ = int(message[5])
            self.own_num = random.randint(3,self.prime-1)
            self.own_publ = pow(self.p_root,self.own_num)%self.prime
            temp = self.own_nick + ','+str(self.own_publ)+'\n'
            time.sleep(1)
            self.ser.write(temp.encode('utf-8'))
            self.listen_for_ok()
        else:
            self.is_connected = False

    def listen_for_ok(self):
        message = ''
        for i in range(0,100):
            m = self.serseri2.read()
            m = int.from_bytes(m,"big")
            if m>=20:
                message = message +chr(m)
            elif m == 10:
                if message == 'OK':
                    self.Key = pow(self.ot_publ,self.own_num)%self.prime
                    self.Key_inv = self.mod_inverse(self.Key,self.prime)
                    print('Bağlantı Kuruldu!!!')
                    self.is_connected = True
                    self.con_message = ''
                    break
            
            

    def settings_func(self):
        win2 = tk.Tk()
        win2.title('Seçenekler')
        frame1 = tk.Frame(win2)
        frame1.grid(row = 0, column = 0)

        nick_l = tk.Label(frame1,text='İsim: ')
        self.nick_e = tk.Entry(frame1)
        id_l = tk.Label(frame1,text='Kimlik: ')
        self.id_e = tk.Entry(frame1)
        id2_l = tk.Label(frame1,text= 'Karşı Kimlik: ')
        self.id2_e = tk.Entry(frame1)
        prime_l = tk.Label(frame1,text='Asal Sayı: ')
        self.prime_e = tk.Entry(frame1)
        p_root_l = tk.Label(frame1,text='İlkel Kök: ')
        self.p_root_e = tk.Entry(frame1)
        default_bu = tk.Button(frame1,text='Varsayılana Sıfırla',command = self.set_default_func)
        set_bu = tk.Button(frame1,text='Kaydet',command = self.save_func)
        connect_bu= tk.Button(frame1,text= 'Bağlan',command = self.connect_func)
        discon_bu = tk.Button(frame1,text= 'Bağlantıyı Kes')

        self.set_default_func()
        
        nick_l.grid(row=0,column = 0)
        self.nick_e.grid(row=0,column = 1)
        id_l.grid(row=1,column=0)
        self.id_e.grid(row=1,column=1)
        id2_l.grid(row=2,column=0)
        self.id2_e.grid(row=2,column=1)
        prime_l.grid(row=3,column=0)
        self.prime_e.grid(row=3,column=1)
        p_root_l.grid(row=4,column=0)
        self.p_root_e.grid(row=4,column=1)
        default_bu.grid(row=5,column=0)
        set_bu.grid(row=5,column=1)
        discon_bu.grid(row=6,column=0)
        connect_bu.grid(row=6,column=1)

    def set_default_func(self):
        self.own_nick = 'Pi-1'
        self.own_id = 12345678
        self.ot_id = 87654321
        self.prime=24391
        self.p_root = 3
        self.own_num = 367
        self.own_publ = pow(self.p_root,self.own_num)%self.prime

        self.nick_e.delete(0,'end')
        self.id_e.delete(0,'end')
        self.id2_e.delete(0,'end')
        self.prime_e.delete(0,'end')
        self.p_root_e.delete(0,'end')
        
        self.nick_e.insert(0,self.own_nick)
        self.id_e.insert(0,str(self.own_id))
        self.id2_e.insert(0,str(self.ot_id))
        self.prime_e.insert(0,str(self.prime))
        self.p_root_e.insert(0,str(self.p_root))
        
    def save_func(self):
        self.own_nick = self.nick_e.get()
        self.own_id = int(self.id_e.get())
        self.ot_id = int(self.id2_e.get())
        self.prime = int(self.prime_e.get())
        self.p_root = int(self.p_root_e.get())
        self.own_num = random.randint(3,self.prime-1)
        self.own_publ = pow(self.p_root,self.own_num)%self.prime

        self.nick_e.delete(0,'end')
        self.id_e.delete(0,'end')
        self.id2_e.delete(0,'end')
        self.prime_e.delete(0,'end')
        self.p_root_e.delete(0,'end')
        
        self.nick_e.insert(0,self.own_nick)
        self.id_e.insert(0,str(self.own_id))
        self.id2_e.insert(0,str(self.ot_id))
        self.prime_e.insert(0,str(self.prime))
        self.p_root_e.insert(0,str(self.p_root))

    def connect_func(self):
        packet = str(self.ot_id)+','+str(self.own_id)+','
        self.ser.write(packet.encode('utf-8'))
        time.sleep(1)
        packet = self.own_nick+','+str(self.prime)+','
        self.ser.write(packet.encode('utf-8'))
        time.sleep(1)
        packet = str(self.p_root)+','+str(self.own_publ)+'\n'
        self.ser.write(packet.encode('utf-8'))
        
        message = ''
        for i in range(0,100):
            m = self.serseri2.read()
            m = int.from_bytes(m,"big")
            if m>=20:
                message = message +chr(m)
            elif m == 10:
                mes2 = message.split(',')
                self.ot_nick = mes2[0]
                self.ot_publ = int(mes2[1])
                self.Key = pow(self.ot_publ,self.own_num)%self.prime
                self.Key_inv = self.mod_inverse(self.Key,self.prime)
                self.is_connected = True
                print('Bağlantı Kuruldu!!')
                mes = 'OK\n'
                time.sleep(1)
                self.ser.write(mes.encode('utf-8'))
                break
        
        

win = tk.Tk()
win.title('ElGamal Şifreleme Programı')
elgamal = ElGamal(win)
win.mainloop()
