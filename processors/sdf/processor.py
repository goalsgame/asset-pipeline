import converter
import core.qt_image as qt_image


def process_svg(svg_path, output_path, rel_distance, svg_resolution, sdf_resolution):
    img = qt_image.svg_to_image(svg_path, svg_resolution, rel_distance)

    img_array = qt_image.image_to_numpy(img)

    # new_img = numpy_to_image(img_array)
    # new_img.save(output_path)

    sdf = converter.compute_multichannel_sdf(img_array, rel_distance, svg_resolution//sdf_resolution)
    converter.save_image_array(sdf, output_path)
