HoRope
============
#### Cinema 4D Python Plugin  

Python script based plugin that generates setup for animating dynamic ropes.  
Tested on CINEMA 4D R18 and R19

Installation
------------
Clone the project or download the zip file and extract it into the Maxon plugins directory.  
Make sure to preserve folder information while unzipping.

- Windows: C:\Program Files\MAXON\CINEMA 4D R...\plugins\
- MacOS: /Applications/MAXON/CINEMA 4D R.../plugins/

Help and notes
------------

Create HoRope object.  
Place your spline under HoRope object.  
Play with settings.  
Make it editable to use setup with dynamics.  

HoRope uses only one segment of a spline.   
You can select multiple splines and click HoRope button holding "ALT" to generate multiple ropes.  

If you whant your rope behaves more stable:  
In Project settings>Dynamics>Expert
- set Steps per frame to 20 or higher 
- set Maximum Solver iterations per step to 20 or higher
- set error treshold to 3% or less

Contacts
------------
Facebook: https://www.facebook.com/Pasha.kho  
Gmail: pashahomenko@gmail.com  
Vimeo: https://vimeo.com/pashaho

License 
------------
MIT License

Copyright (c) 2018 Pasha Ho

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
