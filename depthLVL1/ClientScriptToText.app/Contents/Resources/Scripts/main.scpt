FasdUAS 1.101.10   ��   ��    k             l     ��  ��    - 'set mySearchFor to {getPhotos, stvList}     � 	 	 N s e t   m y S e a r c h F o r   t o   { g e t P h o t o s ,   s t v L i s t }   
  
 l     ��������  ��  ��        p         ������ 0 posixlogfile PosixlogFile��        p         ������ 0 counter  ��        l     ��������  ��  ��        l    	 ����  r     	    I    ��  
�� .earsffdralis        afdr  m     ��
�� afdrboot  �� ��
�� 
rtyp  m    ��
�� 
TEXT��    o      ���� 0 homedir homeDir��  ��        l  
  ����  r   
      l  
  !���� ! b   
  " # " o   
 ���� 0 homedir homeDir # m     $ $ � % % 8 S c r i p t s R e p o r t : C l i e n t S c r i p t s :��  ��     o      ���� 0 	scriptdir 	ScriptDir��  ��     & ' & l    (���� ( r     ) * ) l    +���� + b     , - , o    ���� 0 homedir homeDir - m     . . � / / 2 S c r i p t s R e p o r t : r e s u l t s . t x t��  ��   * o      ���� 0 
resultsdir 
ResultsDir��  ��   '  0 1 0 l     �� 2 3��   2 O Iset CompletedDir to (homeDir & "ScriptsReport:ScriptsComplete:") as alias    3 � 4 4 � s e t   C o m p l e t e d D i r   t o   ( h o m e D i r   &   " S c r i p t s R e p o r t : S c r i p t s C o m p l e t e : " )   a s   a l i a s 1  5 6 5 l    7���� 7 r     8 9 8 c     : ; : l    <���� < b     = > = o    ���� 0 homedir homeDir > m     ? ? � @ @ : L i b r a r y : W e b S e r v e r : S c r i p t T e x t :��  ��   ; m    ��
�� 
alis 9 o      ���� 0 scripttextdir scripttextDir��  ��   6  A B A l   # C���� C r    # D E D n    ! F G F 1    !��
�� 
psxp G o    ���� 0 
resultsdir 
ResultsDir E o      ���� 0 posixlogfile PosixlogFile��  ��   B  H I H l  $ + J���� J r   $ + K L K l  $ ) M���� M b   $ ) N O N b   $ ' P Q P m   $ % R R � S S  " Q o   % &���� 0 posixlogfile PosixlogFile O m   ' ( T T � U U  "��  ��   L o      ���� 0 posixlogfile PosixlogFile��  ��   I  V W V l  , 3 X���� X r   , 3 Y Z Y m   , / [ [ � \ \  * C l i e n t   S c r i p t s Z o      ���� 0 volname volName��  ��   W  ] ^ ] l     �� _ `��   _  tell application "Finder"    ` � a a 2 t e l l   a p p l i c a t i o n   " F i n d e r " ^  b c b l     �� d e��   d 
 	try    e � f f  	 t r y c  g h g l     �� i j��   i L F		mount volume "afp://scripting:alaska@macserver.tmsgf.trb/" & volName    j � k k � 	 	 m o u n t   v o l u m e   " a f p : / / s c r i p t i n g : a l a s k a @ m a c s e r v e r . t m s g f . t r b / "   &   v o l N a m e h  l m l l     �� n o��   n  	end try    o � p p  	 e n d   t r y m  q r q l     �� s t��   s 3 -move every item of scripttextDir to trashgfrt    t � u u Z m o v e   e v e r y   i t e m   o f   s c r i p t t e x t D i r   t o   t r a s h g f r t r  v w v l     �� x y��   x . (move every item of CompletedDir to trash    y � z z P m o v e   e v e r y   i t e m   o f   C o m p l e t e d D i r   t o   t r a s h w  { | { l     �� } ~��   } + %move every item of ScriptDir to trash    ~ �   J m o v e   e v e r y   i t e m   o f   S c r i p t D i r   t o   t r a s h |  � � � l     �� � ���   �  if ResultsDir exists then    � � � � 2 i f   R e s u l t s D i r   e x i s t s   t h e n �  � � � l     �� � ���   � 
 else    � � � �  e l s e �  � � � l     �� � ���   � E ?	set createLogFile to do shell script ("cat > " & PosixlogFile)    � � � � ~ 	 s e t   c r e a t e L o g F i l e   t o   d o   s h e l l   s c r i p t   ( " c a t   >   "   &   P o s i x l o g F i l e ) �  � � � l     �� � ���   � @ :	do shell script ("chmod ugo+rwx " & " & PosixlogFile & ")    � � � � t 	 d o   s h e l l   s c r i p t   ( " c h m o d   u g o + r w x   "   &   "   &   P o s i x l o g F i l e   &   " ) �  � � � l     �� � ���   �  end if    � � � �  e n d   i f �  � � � l     �� � ���   �  end tell    � � � �  e n d   t e l l �  � � � l     �� � ���   � ; 5set saveTo to (homeDir & "ScriptsReport:ScriptText:")    � � � � j s e t   s a v e T o   t o   ( h o m e D i r   &   " S c r i p t s R e p o r t : S c r i p t T e x t : " ) �  � � � l     �� � ���   � � �set clientFolders to {"*BOOKS A-C:", "*BOOKS D-G:", "*BOOKS H-K:", "*BOOKS L-M:", "*BOOKS N-P:", "*BOOKS Q-S:", "*BOOKS T-Z:", "*MILWAUKEE:"} as list    � � � �* s e t   c l i e n t F o l d e r s   t o   { " * B O O K S   A - C : " ,   " * B O O K S   D - G : " ,   " * B O O K S   H - K : " ,   " * B O O K S   L - M : " ,   " * B O O K S   N - P : " ,   " * B O O K S   Q - S : " ,   " * B O O K S   T - Z : " ,   " * M I L W A U K E E : " }   a s   l i s t �  � � � l     �� � ���   � $ repeat with i in clientFolders    � � � � < r e p e a t   w i t h   i   i n   c l i e n t F o l d e r s �  � � � l     �� � ���   � = 7set copyFrom to "Volumes:*Client Scripts:" & i as alias    � � � � n s e t   c o p y F r o m   t o   " V o l u m e s : * C l i e n t   S c r i p t s : "   &   i   a s   a l i a s �  � � � l     �� � ���   �  tell application "Finder"    � � � � 2 t e l l   a p p l i c a t i o n   " F i n d e r " �  � � � l     �� � ���   � P Jduplicate every item of folder copyFrom to folder ScriptDir with replacing    � � � � � d u p l i c a t e   e v e r y   i t e m   o f   f o l d e r   c o p y F r o m   t o   f o l d e r   S c r i p t D i r   w i t h   r e p l a c i n g �  � � � l     �� � ���   �  end tell    � � � �  e n d   t e l l �  � � � l     �� � ���   �  
end repeat    � � � �  e n d   r e p e a t �  � � � l     �� � ���   � - 'repeat with thisFolder in clientFolders    � � � � N r e p e a t   w i t h   t h i s F o l d e r   i n   c l i e n t F o l d e r s �  � � � l     �� � ���   �  tell application "Finder"    � � � � 2 t e l l   a p p l i c a t i o n   " F i n d e r " �  � � � l  4 A ����� � r   4 A � � � l  4 = ����� � I  4 =�� � �
�� .earslfdrutxt  @    file � o   4 5���� 0 	scriptdir 	ScriptDir � �� ���
�� 
lfiv � m   8 9��
�� boovfals��  ��  ��   � o      ���� 0 
folderlist 
folderList��  ��   �  � � � l     ��������  ��  ��   �  � � � l  B M ����� � r   B M � � � c   B I � � � o   B E���� 0 
folderlist 
folderList � m   E H��
�� 
list � o      ���� 0 
folderlist 
folderList��  ��   �  � � � l  N S ����� � r   N S � � � m   N O����   � o      ���� 0 counter  ��  ��   �  � � � l  TA ����� � X   TA ��� � � k   j< � �  � � � l  j j��������  ��  ��   �  � � � O   j z � � � r   p y � � � c   p u � � � b   p s � � � o   p q���� 0 	scriptdir 	ScriptDir � o   q r���� 0 i   � m   s t��
�� 
alis � o      ���� 0 thisfile thisFile � m   j m � �                                                                                   MACS  alis    �  Macintosh HD - C02P61HGG3QNӣʑH+     �
Finder.app                                                      \f�6;�        ����  	                CoreServices    Ӥ�      �6s�       �   x   w  EMacintosh HD - C02P61HGG3QN:System: Library: CoreServices: Finder.app    
 F i n d e r . a p p  8  M a c i n t o s h   H D   -   C 0 2 P 6 1 H G G 3 Q N  &System/Library/CoreServices/Finder.app  / ��   �  � � � l  { {�� � ���   � / )set showScript to ScriptDir & i as string    � � � � R s e t   s h o w S c r i p t   t o   S c r i p t D i r   &   i   a s   s t r i n g �  �  � r   { � c   { � b   { ~ o   { |���� 0 scripttextdir scripttextDir o   | }���� 0 i   m   ~ ��
�� 
TEXT o      ���� 0 
textscript 
textScript   O   �	
	 Q   � k   � �  l  � �����   � |tell application "System Events" to if exists process "Script Editor" then set visible of process "Script Editor" to false		    � � t e l l   a p p l i c a t i o n   " S y s t e m   E v e n t s "   t o   i f   e x i s t s   p r o c e s s   " S c r i p t   E d i t o r "   t h e n   s e t   v i s i b l e   o f   p r o c e s s   " S c r i p t   E d i t o r "   t o   f a l s e 	 	 �� Z   � ����� F   � � H   � � C   � � o   � ����� 0 i   m   � � �  z z z H   � � C   � �  o   � ����� 0 i    m   � �!! �"" * T H U N D E R   B A Y   B 0 H   Q 6   A P k   � �## $%$ l  � ���&'��  & " display dialog contents of i   ' �(( 8 d i s p l a y   d i a l o g   c o n t e n t s   o f   i% )*) l  � ���+,��  + 7 1if i is not equal to "THUNDER BAY B0H Q6 AP" then   , �-- b i f   i   i s   n o t   e q u a l   t o   " T H U N D E R   B A Y   B 0 H   Q 6   A P "   t h e n* ./. r   � �010 I  � ���23
�� .aevtodocnull  �    alis2 o   � ����� 0 thisfile thisFile3 ��4���� 0 showing  4 m   � ���
�� boovfals��  1 o      ���� 0 openthis openThis/ 565 l  � ��78�  7 ( "set scriptName to name of openThis   8 �99 D s e t   s c r i p t N a m e   t o   n a m e   o f   o p e n T h i s6 :;: r   � �<=< n   � �>?> m   � ��~
�~ 
ctxt? o   � ��}�} 0 openthis openThis= o      �|�| 0 mysctext mySCtext; @A@ I  � ��{BC
�{ .coresavenull���    obj B o   � ��z�z 0 openthis openThisC �yDE
�y 
fltpD m   � �FF �GG  t e x tE �xHI
�x 
kfilH o   � ��w�w 0 
textscript 
textScriptI �vJ�u�v 0 	overwrite  J m   � ��t
�t boovtrue�u  A K�sK I  � ��rL�q
�r .coreclosnull���    obj L o   � ��p�p 0 openthis openThis�q  �s  ��  ��  ��   R      �o�n�m
�o .ascrerr ****      � ****�n  �m   k   �MM NON r   � �PQP F   � �RSR m   � �TT �UU \ T h e r e   i s   a   p r o b l e m   w i t h   t h e   f o l l o w i n g   s c r i p t :  S o   � ��l�l 0 openthis openThisQ o      �k�k 0 message  O V�jV I  ��iW�h
�i .sysonotfnull��� ��� TEXTW o   ��g�g 0 message  �h  �j  
 m   � �XX
                                                                                  ToyS  alis    �  Macintosh HD - C02P61HGG3QNӣʑH+     �Script Editor.app                                               W�Ͼn        ����  	                	Utilities     Ӥ�      ϾU�       �   �  FMacintosh HD - C02P61HGG3QN:Applications: Utilities: Script Editor.app  $  S c r i p t   E d i t o r . a p p  8  M a c i n t o s h   H D   -   C 0 2 P 6 1 H G G 3 Q N  (Applications/Utilities/Script Editor.app  / ��   YZY l �f[\�f  [   	tell application "Finder"   \ �]] 4 	 t e l l   a p p l i c a t i o n   " F i n d e r "Z ^_^ l �e`a�e  ` 9 3		duplicate thisFile to CompletedDir with replacing   a �bb f 	 	 d u p l i c a t e   t h i s F i l e   t o   C o m p l e t e d D i r   w i t h   r e p l a c i n g_ cdc l �def�d  e  		quit   f �gg  	 	 q u i td hih l �cjk�c  j  		end tell   k �ll  	 e n d   t e l li mnm Z  0op�b�ao l q�`�_q ?  rsr o  �^�^ 0 counter  s m  �]�] 2�`  �_  p k  ,tt uvu O  wxw I �\�[�Z
�\ .aevtquitnull��� ��� null�[  �Z  x m  yy
                                                                                  ToyS  alis    �  Macintosh HD - C02P61HGG3QNӣʑH+     �Script Editor.app                                               W�Ͼn        ����  	                	Utilities     Ӥ�      ϾU�       �   �  FMacintosh HD - C02P61HGG3QN:Applications: Utilities: Script Editor.app  $  S c r i p t   E d i t o r . a p p  8  M a c i n t o s h   H D   -   C 0 2 P 6 1 H G G 3 Q N  (Applications/Utilities/Script Editor.app  / ��  v z{z r  $|}| m   �Y�Y  } o      �X�X 0 counter  { ~�W~ I %,�V�U
�V .sysodelanull��� ��� nmbr m  %(�T�T �U  �W  �b  �a  n ��� r  1:��� [  16��� o  14�S�S 0 counter  � m  45�R�R � o      �Q�Q 0 counter  � ��P� l ;;�O�N�M�O  �N  �M  �P  �� 0 i   � o   W Z�L�L 0 
folderlist 
folderList��  ��   � ��� l     �K�J�I�K  �J  �I  � ��� l BJ��H�G� O  BJ�F��F  � m  BE��                                                                                   MACS  alis    �  Macintosh HD - C02P61HGG3QNӣʑH+     �
Finder.app                                                      \f�6;�        ����  	                CoreServices    Ӥ�      �6s�       �   x   w  EMacintosh HD - C02P61HGG3QN:System: Library: CoreServices: Finder.app    
 F i n d e r . a p p  8  M a c i n t o s h   H D   -   C 0 2 P 6 1 H G G 3 Q N  &System/Library/CoreServices/Finder.app  / ��  �H  �G  � ��� l KW��E�D� O  KW��� I QV�C�B�A
�C .aevtquitnull��� ��� null�B  �A  � m  KN��
                                                                                  ToyS  alis    �  Macintosh HD - C02P61HGG3QNӣʑH+     �Script Editor.app                                               W�Ͼn        ����  	                	Utilities     Ӥ�      ϾU�       �   �  FMacintosh HD - C02P61HGG3QN:Applications: Utilities: Script Editor.app  $  S c r i p t   E d i t o r . a p p  8  M a c i n t o s h   H D   -   C 0 2 P 6 1 H G G 3 Q N  (Applications/Utilities/Script Editor.app  / ��  �E  �D  � ��� l Xt��@�?� Q  Xt���>� O  [k��� I aj�=��<
�= .fndremptnull��� ��� obj � 1  af�;
�; 
trsh�<  � m  [^��                                                                                   MACS  alis    �  Macintosh HD - C02P61HGG3QNӣʑH+     �
Finder.app                                                      \f�6;�        ����  	                CoreServices    Ӥ�      �6s�       �   x   w  EMacintosh HD - C02P61HGG3QN:System: Library: CoreServices: Finder.app    
 F i n d e r . a p p  8  M a c i n t o s h   H D   -   C 0 2 P 6 1 H G G 3 Q N  &System/Library/CoreServices/Finder.app  / ��  � R      �:�9�8
�: .ascrerr ****      � ****�9  �8  �>  �@  �?  � ��� l     �7���7  �  
end repeat   � ���  e n d   r e p e a t� ��� l     �6�5�4�6  �5  �4  � ��3� l     �2�1�0�2  �1  �0  �3       �/���/  � �.
�. .aevtoappnull  �   � ****� �-��,�+���*
�- .aevtoappnull  �   � ****� k    t��  ��  ��  &��  5��  A��  H��  V��  ���  ���  ���  ��� ��� ��� ��)�)  �,  �+  � �(�( 0 i  � 8�'�&�%�$�# $�" .�! ?� ��� R T [��������� ���X!�������F�
�	�����T���� ��������
�' afdrboot
�& 
rtyp
�% 
TEXT
�$ .earsffdralis        afdr�# 0 homedir homeDir�" 0 	scriptdir 	ScriptDir�! 0 
resultsdir 
ResultsDir
�  
alis� 0 scripttextdir scripttextDir
� 
psxp� 0 posixlogfile PosixlogFile� 0 volname volName
� 
lfiv
� .earslfdrutxt  @    file� 0 
folderlist 
folderList
� 
list� 0 counter  
� 
kocl
� 
cobj
� .corecnte****       ****� 0 thisfile thisFile� 0 
textscript 
textScript
� 
bool� 0 showing  
� .aevtodocnull  �    alis� 0 openthis openThis
� 
ctxt� 0 mysctext mySCtext
� 
fltp
�
 
kfil�	 0 	overwrite  � 
� .coresavenull���    obj 
� .coreclosnull���    obj �  �  � 0 message  
� .sysonotfnull��� ��� TEXT� 2
�  .aevtquitnull��� ��� null�� 
�� .sysodelanull��� ��� nmbr
�� 
trsh
�� .fndremptnull��� ��� obj �*u���l E�O��%E�O��%E�O��%�&E�O��,E�O��%�%E�Oa E` O�a fl E` O_ a &E` OjE` O �_ [a a l kh  a  Ơ%�&E` UOˠ%�&E` Oa  } \�a 	 �a a  & B_ a !fl "E` #O_ #a $-E` %O_ #a &a 'a (_ a )ea * +O_ #j ,Y hW  X - .a /	 	_ #a  &E` 0O_ 0j 1UO_ a 2 a  *j 3UOjE` Oa 4j 5Y hO_ kE` OP[OY�(Oa  hUOa  *j 3UO a  *a 6,j 7UW X - .h ascr  ��ޭ