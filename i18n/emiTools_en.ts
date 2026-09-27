<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="en">
<context>
    <name>@default</name>
    <message>
        <location filename="../emi_tools_util.py" line="71"/>
        <source>Could not create directory {}: {}</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../emi_tools_util.py" line="135"/>
        <source>Error saving file {}: {}</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../emi_tools_util.py" line="143"/>
        <source>File saved: {}</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../emi_tools_util.py" line="165"/>
        <source>Compressed file created: {}</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../emi_tools_util.py" line="168"/>
        <source>Failed to create ZIP {}: {}</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../expressions/emi_tools_expression_format_cnpj.py" line="40"/>
        <source>Invalid number. Pass a numeric string as the input parameter.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../expressions/emi_tools_expression_format_cpf.py" line="40"/>
        <source>Invalid number. Please provide an 11-digit numeric string.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../expressions/emi_tools_expression_format_cpf_cnpj.py" line="45"/>
        <source>Invalid number. Pass a numeric string as the input parameter..</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_resolve_overlap_by_priority.py" line="80"/>
        <source>Input layer</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_aggregate_by_boundary.py" line="87"/>
        <source>Identifier field</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_aggregate_by_boundary.py" line="96"/>
        <source>Boundary layer</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_aggregate_by_boundary.py" line="106"/>
        <source>Identifier prefix</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_aggregate_by_boundary.py" line="114"/>
        <source>Keep unmatched portions</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_replace_geometry.py" line="114"/>
        <source>Output layer</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_resolve_overlap_by_priority.py" line="159"/>
        <source>Field &apos;{}&apos; not found in the input layer.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_aggregate_by_boundary.py" line="156"/>
        <source>Reading boundary layer...</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_aggregate_by_boundary.py" line="176"/>
        <source>The boundary layer has no valid geometries.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_aggregate_by_boundary.py" line="180"/>
        <source>Splitting features by boundary...</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_aggregate_by_boundary.py" line="208"/>
        <source>UNNAMED</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_aggregate_by_boundary.py" line="296"/>
        <source>Dissolving features...</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_aggregate_by_boundary.py" line="350"/>
        <source>Adding unmatched portions...</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_aggregate_by_boundary.py" line="377"/>
        <source>{} feature(s) generated.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_aggregate_by_boundary.py" line="379"/>
        <source>{} skipped (empty geometry).</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_aggregate_by_boundary.py" line="381"/>
        <source>{} had no overlap with the boundary layer.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_aggregate_by_boundary.py" line="383"/>
        <source>{} had a partial overlap.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_aggregate_by_boundary.py" line="386"/>
        <source>Unmatched portions were kept as individual features.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_aggregate_by_boundary.py" line="388"/>
        <source>Unmatched portions were discarded.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_aggregate_by_boundary.py" line="408"/>
        <source>Aggregate Features by Boundary</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_ret_to_vector.py" line="524"/>
        <source>Emi Tools</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_aggregate_by_boundary.py" line="417"/>
        <source>Splits input polygons along the boundaries of the reference layer and dissolves the resulting fragments into a single feature for each reference polygon. Output geometries use the input layer&apos;s CRS.

Fragment identifiers are stored in the &apos;{identifier field}_list&apos; field, with &apos;-a&apos;, &apos;-b&apos;, etc. suffixes. Other attributes are aggregated into &apos;{field}_list&apos; fields. Each resulting feature receives a new identifier in &apos;{identifier field}_new&apos;, consisting of the optional prefix and the identifier of the largest fragment.

Portions without overlap with the reference layer can be kept as individual features or discarded, according to the &apos;Keep unmatched portions&apos; option.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_aggregate_by_field.py" line="67"/>
        <source>Group by field</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_aggregate_by_field.py" line="76"/>
        <source>Maximum features per group (0 = unlimited)</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_aggregate_by_field.py" line="87"/>
        <source>Aggregated layer</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_aggregate_by_field.py" line="104"/>
        <source>Field &apos;{}&apos; not found.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_aggregate_by_field.py" line="177"/>
        <source>Constructing aggregated features...</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_aggregate_by_field.py" line="222"/>
        <source>Aggregate Features by Field</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_aggregate_by_field.py" line="231"/>
        <source>Aggregates features by a selected field.
Aggregated attributes are stored as arrays in fields suffixed with &apos;_list&apos;.
</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_batch_photo_export.py" line="65"/>
        <source>Field containing photo path</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_apply_style_geotagged_photos.py" line="85"/>
        <source>Field containing the camera direction</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_apply_style_geotagged_photos.py" line="96"/>
        <source>Configure map tips</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_apply_style_geotagged_photos.py" line="102"/>
        <source>Configure the form attributes for the photo field</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_apply_style_geotagged_photos.py" line="110"/>
        <source>Export the Layer Definition file (QLR)</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_import_geotagged_photos.py" line="98"/>
        <source>Output file</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_apply_style_geotagged_photos.py" line="138"/>
        <source>Input layer is not valid.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_apply_style_geotagged_photos.py" line="148"/>
        <source>Error loading the exported layer.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_apply_style_geotagged_photos.py" line="164"/>
        <source>Layer definition file exported to: {}</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_apply_style_geotagged_photos.py" line="196"/>
        <source>Photos without direction</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_apply_style_geotagged_photos.py" line="203"/>
        <source>Photos with direction</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_apply_style_geotagged_photos.py" line="228"/>
        <source>Photo field &apos;{}&apos; not found in layer.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_apply_style_geotagged_photos.py" line="259"/>
        <source>Error exporting the QLR file: {}</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_apply_style_geotagged_photos.py" line="269"/>
        <source>Apply style to geotagged photo layer</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_apply_style_geotagged_photos.py" line="278"/>
        <source>This algorithm applies custom symbology to a point layer with geotagged photos, distinguishing photos with or without recorded direction. Also allows configuring map tips with image previews, adjusting the photo field to display as an external resource, and exporting a Layer Definition file (QLR).</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_ret_to_vector.py" line="340"/>
        <source>Output folder</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_batch_photo_export.py" line="81"/>
        <source>Move files instead of copying</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_batch_photo_export.py" line="88"/>
        <source>Overwrite existing files</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_batch_photo_export.py" line="119"/>
        <source>Move files is enabled, but no destination folder was selected. To prevent photos from being moved to a temporary folder and lost, processing was stopped. Please select an output folder and run again.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_batch_photo_export.py" line="180"/>
        <source>Batch photo export</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_batch_photo_export.py" line="189"/>
        <source>This algorithm copies or moves image files listed in a field of a vector layer to a destination folder.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_export_kml_rpa.py" line="68"/>
        <source>Export file name field</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_export_terms.py" line="134"/>
        <source>Open output files after executing the algorithm</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_export_kml_rpa.py" line="208"/>
        <source>Export KML files to DJI Pilot</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_export_kml_rpa.py" line="217"/>
        <source>This algorithm exports each feature from a polygon or line layer to a separate KML file, compatible with software DJI Pilot.&lt;br&gt; To ensure compatibility with the DJI Pilot app, the &amp;lt;Folder&amp;gt; tag ( automatically added by QGIS to structure KML content) is removed, as it is not supported by the application.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_export_terms.py" line="77"/>
        <source>Embargo term field</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_export_terms.py" line="88"/>
        <source>Embargo term series field</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_ret_to_vector.py" line="346"/>
        <source>Output file extension</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_export_terms.py" line="116"/>
        <source>Export all features to a single file</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_export_terms.py" line="125"/>
        <source>Compress output file copy (.zip)</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_export_terms.py" line="213"/>
        <source>Duplicate embargo term numbers found: {}</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_export_terms.py" line="275"/>
        <source>Field &apos;NUM_TEI&apos; not found in the layer after renaming.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_export_terms.py" line="284"/>
        <source>Skipping feature {} due to empty &apos;NUM_TEI&apos; value.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_export_terms.py" line="306"/>
        <source>Saved file: {}</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_export_terms.py" line="308"/>
        <source>Error saving file for TEI {}: {}</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_export_terms.py" line="312"/>
        <source>Total number of saved files: {}</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_export_terms.py" line="346"/>
        <source>Export polygons to SICAFI</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_export_terms.py" line="355"/>
        <source>This algorithm exports features from a polygon layer to individual or single vector files, compatible with the upload of embargoed areas to the Cadastro, Arrecadação e Fiscalização System (Sicafi). The algorithm removes unnecessary fields, renames mandatory fields to 'NUM_TEI' and 'SERIE_TEI', and offers the option to compress the output files into a ZIP archive.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_photo_stamp_rpa.py" line="90"/>
        <source>Input folder</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_import_geotagged_photos.py" line="102"/>
        <source>Scan recursively</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_import_geotagged_photos.py" line="118"/>
        <source>Metadata to import</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_import_geotagged_photos.py" line="131"/>
        <source>Extract all available EXIF/XMP tags</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_import_geotagged_photos.py" line="142"/>
        <source>Add &quot;description&quot; field to the output file</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_import_geotagged_photos.py" line="154"/>
        <source>Add &quot;selected&quot; field to the output file</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_import_geotagged_photos.py" line="214"/>
        <source>Found {} images to process.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_import_geotagged_photos.py" line="231"/>
        <source>No geotag found</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_import_geotagged_photos.py" line="234"/>
        <source>Error processing {}: {}</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_import_geotagged_photos.py" line="268"/>
        <source>A total of {} images with geotags and {} images without geotags were identified.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_import_geotagged_photos.py" line="347"/>
        <source>Import geotagged photos from DJI drones</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_import_geotagged_photos.py" line="356"/>
        <source>This algorithm generates a point layer based on georeferenced locations (geotags) extracted from JPEG images in a source folder.It supports both standard EXIF metadata and specific tags used by DJI drones. In the advanced options, you can choose to extract all available tags and add auxiliary fields.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_photo_stamp_rpa.py" line="98"/>
        <source>SVG Image</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_photo_stamp_rpa.py" line="104"/>
        <source>Text</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_photo_stamp_rpa.py" line="122"/>
        <source>Metadata to stamp</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_photo_stamp_rpa.py" line="136"/>
        <source>Bottom Left</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_photo_stamp_rpa.py" line="137"/>
        <source>Bottom Right</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_photo_stamp_rpa.py" line="138"/>
        <source>Top Left</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_photo_stamp_rpa.py" line="139"/>
        <source>Top Right</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_photo_stamp_rpa.py" line="143"/>
        <source>Position of text and image</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_photo_stamp_rpa.py" line="162"/>
        <source>Font</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_photo_stamp_rpa.py" line="171"/>
        <source>Font color</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_photo_stamp_rpa.py" line="181"/>
        <source>Percentage (%)</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_photo_stamp_rpa.py" line="182"/>
        <source>Pixels (px)</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_photo_stamp_rpa.py" line="183"/>
        <source>Centimeters (cm)</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_photo_stamp_rpa.py" line="184"/>
        <source>Millimeters (mm)</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_photo_stamp_rpa.py" line="185"/>
        <source>Inches (pol)</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_photo_stamp_rpa.py" line="189"/>
        <source>Stamp height unit</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_photo_stamp_rpa.py" line="201"/>
        <source>Stamp height value</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_photo_stamp_rpa.py" line="215"/>
        <source>Margin from edge</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_photo_stamp_rpa.py" line="278"/>
        <source>Failed to load input image: {}</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_photo_stamp_rpa.py" line="329"/>
        <source>Image saved at {}</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_photo_stamp_rpa.py" line="421"/>
        <source>Failed to load SVG file: {}</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_photo_stamp_rpa.py" line="481"/>
        <source>Could not write tag {}: {}</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_photo_stamp_rpa.py" line="504"/>
        <source>Stamp text and image on the photo</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_photo_stamp_rpa.py" line="513"/>
        <source>This algorithm inscribes text and an optional SVG logo onto JPEG or PNG images using EXIF metadata such as coordinates, altitude, date, and camera model. The stamp height is defined by the user in %, px or cm, and the font size adjusts automatically. The processed images are saved in the output folder, preserving EXIF data.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_replace_geometry.py" line="69"/>
        <source>Target layer</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_replace_geometry.py" line="77"/>
        <source>Target field</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_replace_geometry.py" line="86"/>
        <source>Source layer</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_replace_geometry.py" line="94"/>
        <source>Source field</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_replace_geometry.py" line="103"/>
        <source>Update other common attributes</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_replace_geometry.py" line="150"/>
        <source>Field &apos;{}&apos; not found in the target layer.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_replace_geometry.py" line="156"/>
        <source>Field &apos;{}&apos; not found in the source layer.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_replace_geometry.py" line="171"/>
        <source>Geometry type mismatch: the target layer is &apos;{}&apos; but the source layer is &apos;{}&apos;. Both layers must have the same geometry category (point/line/polygon), and a multi-part source cannot be used with a single-part target.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_replace_geometry.py" line="184"/>
        <source>Indexing source layer features...</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_replace_geometry.py" line="199"/>
        <source>Duplicate keys found in source layer: {}. Please ensure the source layer has unique values in the common field before running this algorithm.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_replace_geometry.py" line="207"/>
        <source>{} unique keys indexed from the source layer (feature count reported by the source: {}).</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_replace_geometry.py" line="223"/>
        <source>Common attributes to be updated: {}</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_replace_geometry.py" line="223"/>
        <source>No common attributes found besides the join fields.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_replace_geometry.py" line="268"/>
        <source>No matching feature found in source layer for key &apos;{}&apos; (feature id {}). Original geometry kept.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_replace_geometry.py" line="278"/>
        <source>Finished. {} geometries replaced, {} features kept unchanged (no match).</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_replace_geometry.py" line="303"/>
        <source>Replace feature geometry</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_replace_geometry.py" line="312"/>
        <source>This algorithm replaces the geometry of features in a target layer with the geometry of matching features from a source layer, based on a common field between the two layers.

Features in the target layer that have no matching key in the source layer keep their original geometry, and a warning is reported.

Advanced option: &apos;Update other common attributes&apos; also copies over the values of any attribute that has the same name in both layers.

</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_resolve_overlap_by_priority.py" line="88"/>
        <source>Priority field</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_resolve_overlap_by_priority.py" line="97"/>
        <source>Sort order</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_resolve_overlap_by_priority.py" line="108"/>
        <source>Remove fully covered features</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_resolve_overlap_by_priority.py" line="119"/>
        <source>Fix invalid geometries</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_resolve_overlap_by_priority.py" line="130"/>
        <source>Minimum sliver area</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_resolve_overlap_by_priority.py" line="144"/>
        <source>Layer without overlaps</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_resolve_overlap_by_priority.py" line="189"/>
        <source>Reading features...</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_resolve_overlap_by_priority.py" line="206"/>
        <source>{} feature(s) have no value in the priority field and are treated as lowest priority.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_resolve_overlap_by_priority.py" line="215"/>
        <source>Resolving overlaps...</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_resolve_overlap_by_priority.py" line="301"/>
        <source>{} feature(s) fully covered and removed.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_resolve_overlap_by_priority.py" line="305"/>
        <source>{} feature(s) fully covered, kept with empty geometry.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_resolve_overlap_by_priority.py" line="311"/>
        <source>{} feature(s) had a tied priority value with an overlapping feature and were not clipped against it; some overlap may remain.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_resolve_overlap_by_priority.py" line="377"/>
        <source>Resolve Overlaps by Priority Field</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_resolve_overlap_by_priority.py" line="386"/>
        <source>Resolves overlaps within a single polygon layer using a priority field: where two or more features overlap, the one with the top-priority value is kept whole, and the others are clipped to remove the overlapping area.

The priority field accepts date, numeric or text values. The sort order defines whether the highest or the lowest value wins.

Features with no value in the priority field are treated as lowest priority. Features with the same priority value do not clip each other, so some overlap may remain between them; the final report shows how many features were affected.

Advanced options control what happens to fully covered features (removed or kept with an empty geometry), whether invalid geometries are fixed after clipping, and the minimum area for residual sliver polygons to be kept.

The attribute table is preserved; only the geometry of clipped features is changed.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_ret_to_vector.py" line="97"/>
        <source>Field &apos;{}&apos; exceeded {} characters and was truncated to maintain Shapefile compatibility.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_ret_to_vector.py" line="330"/>
        <source>SICAR .RET file</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_ret_to_vector.py" line="355"/>
        <source>Load generated layers into the project</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_ret_to_vector.py" line="368"/>
        <source>Invalid or missing .RET file.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_ret_to_vector.py" line="379"/>
        <source>Reading .RET file...</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_ret_to_vector.py" line="391"/>
        <source>SICAR file not found inside the .RET. Expected a file starting with a state acronym (e.g. &apos;PB-&apos;) or the &apos;CAR&apos; prefix.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_ret_to_vector.py" line="400"/>
        <source>The .RET file is not a valid SICAR export (expected a zip archive).</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_ret_to_vector.py" line="427"/>
        <source>Skipping layer &apos;{}&apos;: geometry is invalid or empty.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_ret_to_vector.py" line="462"/>
        <source>Error saving &apos;{}&apos;: {}</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_ret_to_vector.py" line="465"/>
        <source>Saved: {}</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_ret_to_vector.py" line="468"/>
        <source>{} of {} layer(s) written successfully.</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_ret_to_vector.py" line="481"/>
        <source>Could not reload layer: {}</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_ret_to_vector.py" line="521"/>
        <source>Convert SICAR .RET to vector layers</source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_ret_to_vector.py" line="530"/>
        <source>Converts a SICAR .RET export into individual vector layers. Each geometry type is saved as a separate vector file, and all generated layers receive the property&apos;s cadastral information as attribute fields. </source>
        <translation></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_assign_raster_name.py" line="99"/>
        <source>Raster layers</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_assign_raster_name.py" line="107"/>
        <source>Output field</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_assign_raster_name.py" line="118"/>
        <source>Use each raster&apos;s data footprint instead of its bounding box</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_assign_raster_name.py" line="129"/>
        <source>Discard candidates mostly covered by a black/nodata border</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_assign_raster_name.py" line="140"/>
        <source>Pixel value considered black/nodata</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_assign_raster_name.py" line="165"/>
        <source>No raster layers were provided.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_assign_raster_name.py" line="178"/>
        <source>GDAL&apos;s Footprint tool is not available in this installation (requires GDAL 3.8+); using the raster bounding box for all rasters instead.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_assign_raster_name.py" line="203"/>
        <source>Reading raster bounding boxes...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_assign_raster_name.py" line="254"/>
        <source>Field &apos;{}&apos; has a maximum length of {} characters, but the following raster name(s) are longer and may be truncated by the data provider: {}.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_assign_raster_name.py" line="263"/>
        <source>The following raster(s) cannot be read for the black/nodata border check and will be matched by geometry only: {}.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_assign_raster_name.py" line="272"/>
        <source>The following raster(s) already declare a nodata value in their own metadata; the black/nodata border check is skipped for them as redundant: {}.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_assign_raster_name.py" line="295"/>
        <source>Could not compute the data footprint for raster &apos;{}&apos; ({}); using its bounding box instead.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_assign_raster_name.py" line="312"/>
        <source>Matching features to rasters...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_assign_raster_name.py" line="379"/>
        <source>{} feature(s) matched, {} without an overlapping raster.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_assign_raster_name.py" line="385"/>
        <source>{} candidate(s) were discarded for being mostly black/nodata (last one: &apos;{}&apos;).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_assign_raster_name.py" line="392"/>
        <source>{} pixel sample(s) could not be read; the affected candidates were accepted without a black-border check.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_assign_raster_name.py" line="416"/>
        <source>GDAL Footprint returned no result</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_assign_raster_name.py" line="421"/>
        <source>could not read the footprint output</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_assign_raster_name.py" line="429"/>
        <source>no valid footprint geometry</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_assign_raster_name.py" line="469"/>
        <source>could not read raster pixel data</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_assign_raster_name.py" line="497"/>
        <source>Assign Raster Name by Overlap</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../provider/emi_tools_assign_raster_name.py" line="506"/>
        <source>Matches each input polygon against a set of raster layers, and writes the name of the raster with the greatest overlapping area into an existing attribute field. Features with no overlapping raster get an empty value.

By default, matching uses each raster&apos;s bounding box. The advanced option &apos;Use each raster&apos;s data footprint instead of its bounding box&apos; computes the actual data extent (excluding nodata borders declared in the raster&apos;s own metadata) via GDAL&apos;s footprint tool; this requires GDAL 3.8+ and is slower, since each raster&apos;s pixel mask has to be read. The footprint is only computed for rasters whose bounding box actually overlaps some input feature, and only once per raster (cached for reuse). If unavailable, or if it fails for a specific raster, the bounding box is used instead and a warning is shown.

The advanced option &apos;Discard candidates mostly covered by a black/nodata border&apos; samples a small, fixed-size grid of pixels (kept small on purpose, regardless of raster resolution) inside each candidate&apos;s overlap area, comparing them against the &apos;Pixel value considered black/nodata&apos; value you set. This is meant for imagery whose nodata border isn&apos;t declared in its metadata (so &apos;Use footprint&apos; would not detect it), such as many satellite quicklook composites: a black corner isn&apos;t flagged as nodata by the file itself, only by its pixel value. If a candidate is mostly black/nodata, it is discarded and the next best-overlapping candidate is tried. Rasters that already declare a nodata value in their own metadata skip this check, since it would be redundant; rasters that cannot be read are also matched by geometry only. Both cases are reported.

The output field must already exist in the input layer; behavior is the same whether the algorithm is run normally or with &apos;Edit features in-place&apos;. If the field has a defined maximum length shorter than some raster names, a warning is shown listing which names may be truncated by the data provider.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
</TS>
