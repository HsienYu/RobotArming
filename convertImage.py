# -*- coding: utf-8 -*-
import cairosvg

svg = 'output/out.svg'
png = 'output/out.png'
cairosvg.svg2png(url=svg, write_to=png, parent_width=750, parent_height=1000)

