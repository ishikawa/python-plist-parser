/**
 * core_foundation_parser.c
 * 
 * Parse specified property list xml.
 *
 */
#include <CoreFoundation/CoreFoundation.h>
#include <stdio.h>
#include <stdlib.h>



static CFPropertyListRef createPropertyListWithData(CFDataRef resourceData) {
  CFReadStreamRef stream = NULL;
  CFPropertyListFormat format = kCFPropertyListXMLFormat_v1_0;
  CFPropertyListRef propertyList = NULL;

  stream = CFReadStreamCreateWithBytesNoCopy(kCFAllocatorDefault,
    CFDataGetBytePtr(resourceData),
    CFDataGetLength(resourceData),
    kCFAllocatorNull
  );

  if (!CFReadStreamOpen(stream)) {
    fprintf(stderr, "Failed to open resource\n");
    return NULL;
  }

  propertyList = CFPropertyListCreateFromStream(kCFAllocatorDefault,
    stream, 0,
    kCFPropertyListMutableContainers,
    &format,
    NULL);

  CFReadStreamClose(stream);
  CFRelease(stream);
  return propertyList;
}


static CFURLRef createURLWithCStringFileSystemPath(const char *filepath) {
  CFStringRef pathString = CFStringCreateWithCString(kCFAllocatorDefault, filepath, kCFStringEncodingUTF8);
  CFURLRef fileURL = CFURLCreateWithFileSystemPath(kCFAllocatorDefault,
        pathString,
        kCFURLPOSIXPathStyle,
        false);
  CFRelease(pathString);
  return fileURL;
}

static CFDataRef createDataFromResource(const char *filepath) {
  CFDataRef resourceData = NULL;
  CFURLRef fileURL = createURLWithCStringFileSystemPath(filepath);
  Boolean result = CFURLCreateDataAndPropertiesFromResource(kCFAllocatorDefault,
    fileURL,
    &resourceData,
    NULL,
    NULL,
    NULL);
  CFRelease(fileURL);
  return result ? resourceData : NULL;
}


int main(int argc, const char **argv) {
  const char * filepath = NULL;
  CFDataRef resourceData = NULL;
  long i, times;

  /* Check arguments */
  if (argc < 3) {
    fprintf(stderr, "Usage: %s <filepath> <times>\n", argv[0]);
    return -1;
  }
  filepath = argv[1];
  times = strtol(argv[2], NULL, 10);

  /* Read file contents */
  resourceData = createDataFromResource(filepath);
  if (!resourceData) {
    fprintf(stderr, "Failed to read contents from file %s\n", filepath);
    return -1;
  }

  /* main loop */
  /*fprintf(stderr, "Executing %ld times\n", times);*/
  for (i = 0; i < times; i++) {
    volatile CFPropertyListRef propertyList = createPropertyListWithData(resourceData);
    if (!propertyList) {
      fprintf(stderr, "Failed to create property list from file %s\n", filepath);
      return -1;
    }
    /*
    CFShow(propertyList);
    CFRelease(propertyList);
    */
  }

  CFRelease(resourceData);
  return 0;
}
