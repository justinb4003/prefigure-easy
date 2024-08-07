## Add a graphical element describing a parametric curve

import lxml.etree as ET
from prefigure import user_namespace as un
from prefigure import utilities as util

def parametric_curve(element, diagram, parent, outline_status):
    if outline_status == 'finish_outline':
        finish_outline(element, diagram, parent)
        return

    f = un.valid_eval(element.get('function'))
    domain = un.valid_eval(element.get('domain'))
    N = int(element.get('N', '100'))

    t = domain[0]
    dt = (domain[1]-domain[0])/N
    p = diagram.transform(f(t))
    points = ['M ' + util.pt2str(p)]
    for _ in range(N):
        t += dt
        p = diagram.transform(f(t))
        points.append('L ' + util.pt2str(p))
    if element.get('closed', 'no') == 'yes':
        points.append('Z')
    d = ' '.join(points)

    if diagram.output_format() == 'tactile':
        element.set('stroke', 'black')
        if element.get('fill') is not None:
            element.set('fill', 'lightgray')
    else:
        util.set_attr(element, 'stroke', 'blue')
        util.set_attr(element, 'fill', 'none')
    util.set_attr(element, 'thickness', '2')

    path = ET.Element('path')
    diagram.add_id(path, element.get('id'))
    path.set('d', d)
    util.add_attr(path, util.get_2d_attr(element))
    path.set('type', 'parametric curve')

    element.set('cliptobbox', element.get('cliptobbox', 'yes'))
    util.cliptobbox(path, element, diagram)

    if outline_status == 'add_outline':
        diagram.add_outline(element, path, parent)
        return

    if element.get('outline', 'no') == 'yes' or diagram.output_format() == 'tactile':
        diagram.add_outline(element, path, parent)
        finish_outline(element, diagram, parent)
    else:
        parent.append(path)

def finish_outline(element, diagram, parent):
    diagram.finish_outline(element,
                           element.get('stroke'),
                           element.get('thickness'),
                           element.get('fill', 'none'),
                           parent)
