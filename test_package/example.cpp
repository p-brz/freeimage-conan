#include <FreeImage.h>
#include <FreeImagePlus.h>

#include <string>
#include <iostream>
#include <stdio.h>

using namespace std;

#define NEED_INIT defined(FREEIMAGE_LIB) || !defined(WIN32)

void FreeImageErrorHandler(FREE_IMAGE_FORMAT fif, const char *message) {
    printf("FreeImage error: '%s'\n", message);
}

void testLib(int argc, const char** argv)
{
#if NEED_INIT
    FreeImage_Initialise();
#endif

    FreeImage_SetOutputMessage(FreeImageErrorHandler);
    
    const char * image_file = argc > 1 ? argv[1] : "./test.png";
    fipImage img;
    
    if(img.load(image_file)){
        cout << "Loaded img: '" << image_file 
             << "' with size: (" << img.getWidth() << ", " << img.getHeight() << ")" << endl; 
    }
    else{
        cout << "Failed to loaded img: '" << image_file << endl;
    }
  
#if NEED_INIT
    FreeImage_DeInitialise(); 
#endif   
}

int main(int argc, const char ** argv){
    cout << "************* Testing freeimage lib **************" << endl;

    testLib(argc, argv);
    
    cout << "**************************************************" << endl;

    return 0;
}
