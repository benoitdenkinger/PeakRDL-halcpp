
cmake_minimum_required(VERSION 3.25)

project(PeakRDL-halcpp-Documentation
        VERSION 0.4.0
)

# This is needed to create the python venv for CMinx
include("deps/deps.cmake")

# Check Sphinx executables exists
# find_program(
#     SPHINX_BUILD
#     NAMES sphinx-build
#     HINTS ${Python3_VIRTUAL_ENV}/bin
#     REQUIRED
# )
find_program(
    SPHINX_APIDOC
    NAMES sphinx-apidoc
    HINTS ${Python3_VIRTUAL_ENV}/bin
    REQUIRED
)
# This prints a message saying the executables are found
include(FindPackageHandleStandardArgs)
# find_package_handle_standard_args(Sphinx-build DEFAULT_MSG SPHINX_BUILD)
find_package_handle_standard_args(Sphinx-apidoc DEFAULT_MSG SPHINX_APIDOC)


# Create the API documentation target
set(API_DOC_INPUT_DIR "${PROJECT_SOURCE_DIR}/../src/")
set(API_SPHINX_SRC_DIR "${PROJECT_BINARY_DIR}/api/sphinx_docs/")
set(API_SPHINX_BUILD_DIR "${API_SPHINX_SRC_DIR}/_build/")
# Default location in conf.py
set(SPHINX_TMPL_DIR "${API_SPHINX_SRC_DIR}/_templates/")

# Sphinx is used to convert PeakRDL-halcpp method comments into rST format later transformed to a
# static html documentation using again sphinx
set(API_DOC_RST_CMD ${SPHINX_APIDOC} --full --module-first -a -H ${PROJECT_NAME} -A CERN -R ${PROJECT_VERSION} --templatedir=${SPHINX_TMPL_DIR} -o ${API_SPHINX_SRC_DIR} ${API_DOC_INPUT_DIR})
# This command trigger the rST to html conversion (internally using sphinx-build command)
set(API_DOC_HTML_CMD make -C ${API_SPHINX_SRC_DIR} html)
# This file creates an automatic triggering for the documentation update
set(API_INDEX_HTML_FILE "${API_SPHINX_BUILD_DIR}/html/index.html")

add_custom_command(
        OUTPUT ${API_SPHINX_SRC_DIR}
        COMMAND "${CMAKE_COMMAND}" -E make_directory "${API_SPHINX_SRC_DIR}"
        COMMENT "Create documentation output directory."
)

add_custom_command(
        OUTPUT ${API_INDEX_HTML_FILE}
        COMMAND ${API_DOC_RST_CMD}
        COMMAND ${API_DOC_HTML_CMD}
        DEPENDS ${API_SPHINX_SRC_DIR}
        COMMENT "Generating the PeakRDL-halcpp API rST documentation."
)
# This will trigger the above command through the dependency
add_custom_target(
        api_doc
        DEPENDS ${API_INDEX_HTML_FILE}
)

# Generated files based on cmake configuration/template file (.in files)
# Only @MY_VAR@ format is replaced to avoid replacing structure like ${MY_VAR} which are used in other
# languages or file format (e.g., in Makefiles).
configure_file(${PROJECT_SOURCE_DIR}/sphinx_config/conf.py.in ${SPHINX_TMPL_DIR}/conf.py_t @ONLY)
configure_file(${PROJECT_SOURCE_DIR}/sphinx_config/Makefile.in ${SPHINX_TMPL_DIR}/Makefile_t @ONLY)

# Now build the docusaurus documentation using npm
find_program(NPM_EXECUTABLE npm)
find_package_handle_standard_args(npm DEFAULT_MSG NPM_EXECUTABLE)

set(DOCUSAURUS_OUT_DIR  ${PROJECT_BINARY_DIR}/docusaurus)
file(MAKE_DIRECTORY ${DOCUSAURUS_OUT_DIR})
set(DOCUSAURUS_STAMP_FILE ${DOCUSAURUS_OUT_DIR}/stamp.stamp)
add_custom_command(
        OUTPUT ${DOCUSAURUS_STAMP_FILE}
        WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
        COMMAND touch ${DOCUSAURUS_STAMP_FILE}
        COMMAND ${NPM_EXECUTABLE} install docusaurus
        COMMAND ${NPM_EXECUTABLE} run build ${PROJECT_SOURCE_DIR} -- --out-dir ${DOCUSAURUS_OUT_DIR}
        # API static html is copied and added as a simple link (didn't find a nicer solution yet)
        COMMAND cp -r ${API_SPHINX_BUILD_DIR}/html ${DOCUSAURUS_OUT_DIR}/api_html
        DEPENDS api_doc
        COMMENT "Installing and Building Docusaurus"
)
add_custom_target(docusaurus_doc
        DEPENDS ${DOCUSAURUS_STAMP_FILE}
        COMMENT "Installing and Building Docusaurus"
)

add_custom_target(docusaurus_start
        DEPENDS docusaurus_doc
        COMMAND ${NPM_EXECUTABLE} run serve ${PROJECT_SOURCE_DIR} -- --dir ${DOCUSAURUS_OUT_DIR}
)
