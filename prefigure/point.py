import lxml.etree as ET
import user_namespace as un
import utilities as util
import copy
import label        

# Add a graphical element describing a point
def point(element, diagram, parent, outline_status = None):
    # if we're outlining the shape and have already added the outline,
    # we'll just add the point to complete the task
    if outline_status == 'finish_outline':
        finish_outline(element, diagram, parent)
        return

    # determine the location and size of the point from the XML element
    p = diagram.transform(un.valid_eval(element.get('p')))
    if diagram.output_format() == 'tactile':
        element.set('size', element.get('size', '9'))
    else:
        element.set('size', element.get('size', '4'))
    size = util.get_attr(element, 'size', '1')

    # by default, we'll assume it's a circle but we can change that later
    shape = ET.Element('circle')
    diagram.add_id(shape, element.get('id'))

    # now we'll work out the actual shape of the point
    style = util.get_attr(element, 'style', 'circle')
    if style == 'circle':
        shape.set('cx', util.float2str(p[0]))
        shape.set('cy', util.float2str(p[1]))
        shape.set('r', size)
    size = float(size)
    if style == 'box':
        shape.tag = 'rect'
        shape.set('x', util.float2str(p[0]-size))
        shape.set('y', util.float2str(p[1]-size))
        shape.set('width', util.float2str(2*size))
        shape.set('height', util.float2str(2*size))
    if style == 'diamond':
        shape.tag = 'polygon'
        size *= 1.4
        points = util.pt2str((p[0], p[1]-size), spacer=',')
        points += ' ' + util.pt2str((p[0]+size, p[1]), spacer=',')
        points += ' ' + util.pt2str((p[0], p[1]+size), spacer=',')
        points += ' ' + util.pt2str((p[0]-size, p[1]), spacer=',')
        shape.set('points', points)

    if diagram.output_format() == 'tactile':
        element.set('fill', 'lightgray')
        element.set('stroke', 'black')
    else:
        element.set('fill', util.get_attr(element, 'fill', 'red'))
        element.set('stroke', util.get_attr(element, 'stroke', 'black'))
    element.set('thickness', util.get_attr(element, 'thickness', '2'))
    util.add_attr(shape, util.get_2d_attr(element))
    shape.set('type', 'point')
    util.cliptobbox(shape, element)

    if outline_status == 'add_outline':
        diagram.add_outline(element, shape, parent)
        return

    if element.get('outline', 'no') == 'yes' or diagram.output_format() == 'tactile':
        diagram.add_outline(element, shape, parent)
        finish_outline(element, diagram, parent)
    else:
        parent = add_label(element, diagram, parent)
        parent.append(shape)

def finish_outline(element, diagram, parent):
    parent = add_label(element, diagram, parent)
    diagram.finish_outline(element,
                           element.get('stroke'),
                           element.get('thickness'),
                           element.get('fill', 'none'),
                           parent)

def add_label(element, diagram, parent):
    # Is there a label associated with point?
    text = element.text
    if text is not None or len(element) > 0:
        # If there's a label, we'll bundle the label and point in a group
        group = ET.SubElement(parent, 'g')
        diagram.add_id(group, element.get('id'))
        group.set('type', 'labeled-point')

        # Now we'll create a new XML element describing the label
        el = copy.deepcopy(element)
        el.tag = 'label'
        alignment = util.get_attr(element, 'alignment', 'ne')
        el.set('alignment', alignment)
        size = element.get('size', '4')
        displacement = label.alignment_displacement[alignment]
        el.set('p', util.get_attr(element, 'p', '(0,0)'))

        # Determine how far to offset the label
        # TODO:  improve tactile offsets
        offset = element.get('offset', None)
        if offset is None:
            o = float(size) + 1
            offset = [2*o*(displacement[0]+0.5),
                      2*o*(displacement[1]-0.5)]
            if diagram.output_format() == 'tactile' and offset[0] < 0:
                offset[0] -= 6
        else:
            offset = un.valid_eval(offset)

        el.set('offset', str(offset))

        # add the label graphical element to the group
        label.label(el, diagram, group)
        return group
    else:
        return parent