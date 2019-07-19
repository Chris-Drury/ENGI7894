#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <math.h>

// #ifdef __APPLE__
// #include <OpenCL/opencl.h>
// #else
// #include <CL/cl.hpp>
// #endif

// #define CL ENABLE_EXCEPTIONS
// #define MAX_SOURCE_SIZE (0x100000)

using namespace std;

struct Whale
{
    vector<int> xList;
    vector<int> yList;
    float distance = 0;
    
};

void determineLocations(vector<Whale> &points) {
    // do the magic work
    cout << "the size is : ";
    int pSize = points.size();
    cout << "\n distances: \n";

    // determine the distances
    for (int i = 0; i < pSize; i++){
        Whale point = points[i];
        float x1 = 0;
        float y1 = 0;

        int vSize = point.xList.size();
        
        for (int j = 0; j < vSize; j++) {
            if (j == 0) {
                float x2 = point.xList[j];
                float y2 = point.yList[j];
                point.distance += sqrt((x2-0)*(x2-0)+(y2-0)*(y2-0));
            } else {
                float x2 = point.xList[j];
                float y2 = point.yList[j];
                point.distance += sqrt((x2-point.xList[j-1])*(x2-point.xList[j-1])+(y2-point.yList[j-1])*(y2-point.yList[j-1])); 
            }
        }
        points[i] = point;
    }

    // reorder the points
    for (int i = 0; i < pSize; i++) {
        float minDist = points[i].distance;
        int minIdx = i;
        for (int j = i+1; j < pSize; j++) {
            float dist = points[j].distance;

            if (dist < minDist) {
                cout << dist << " < " << minDist << " \n";
                minIdx = j;
            }
        }

        Whale tmp = points[i];
        points[i] = points[minIdx];
        points[minIdx] = tmp;
    }

    cout << "ordered points: \n";
    for (int i = 0; i < pSize; i++) {
        cout << i << " : " << points[i].distance << "\n";
    }
}

// void createKernel(vector<Whale> points) {
//     // create a kernel

//     FILE *fp;
// 	char fileName[] = "./kernelWork.cl";
// 	char *source_str;
// 	size_t source_size;

// 	/* Load the source code containing the kernel*/
// 	fp = fopen(fileName, "r");
// 	if (!fp) {
// 		fprintf(stderr, "Failed to load kernel.\n");
// 		exit(1);
// 	}

// 	source_str = (char*)malloc(MAX_SOURCE_SIZE);
// 	source_size = fread(source_str, 1, MAX_SOURCE_SIZE, fp);
// 	fclose(fp);
        
//     // 1. Get a platform.
//     cl_platform_id platform;
//     clGetPlatformIDs( 1, &platform, NULL );

//     // 2. Find a gpu device.
//     cl_device_id device;
//     clGetDeviceIDs(platform, CL_DEVICE_TYPE_GPU, 1, &device, NULL);

//     cl::Context context = cl::Context(NULL, 1, &device, NULL, NULL, NULL);

//     std::vector<cl::Device> devices = context.getInfo<CL_CONTEXT_DEVICES>();

//     cl::CommandQueue queue = cl::CommandQueue(context, devices[0]);

//     cl::Buffer bufP = cl::Buffer(context, CL_MEM_READ_ONLY | CL_MEM_COPY_HOST_PTR, sizeof(points), &points);

//     cl::Program::Sources sources(2, std::make_pair(source_str, source_size));

//     cl::Program program = cl::Program(context, sources);
//     program.build(devices);

//     cl::Kernel kernel = cl::Kernel(program, "Assignment");

//     //set the kernel args
//     kernel.setArg(0, bufP);

//     queue.enqueueNDRangeKernel(kernel, cl::NDRange(), cl::NDRange(sizeof(points)), cl::NDRange(64));

// }



int main(int argc, char *argv[]) {
    vector<Whale> points;
    cout << "Arguments:\n";

    // ensure the required args are passed in
    if (argc == 3) {
        for (int i = 0; i < argc; ++i) 
            cout << argv[i] << "\n"; 

        cout << "\n\nThe input is:\n";

        // read the input file
        ifstream input_ (argv[1], ifstream::in);
        
        // get the first char (number of whales)
        int maxCnt;
        input_ >> maxCnt;

        // get the number of stops on each trajectory
        int maxTraj;
        input_ >> maxTraj;

        int c;
        // parse each line and store the data into the vector
        for (int cnt = 0; cnt < maxCnt; cnt++) {
            Whale cart;
            for (int traj = 0; traj < maxTraj; traj++) {
                input_ >> c;
                cart.xList.push_back(c);  //add the x coordinate

                std::cout << c << ",";

                input_ >> c;
                cart.yList.push_back(c);  //add the y coordinate

                std::cout << c << " | ";
            
            }
            cout << "\n";
            points.push_back(cart);
        }
        determineLocations(points);

        // create the Kernel and preform the operation
        //createKernel();

        // write the output to the output.txt file
        ofstream outputFile (argv[2]);
        if (outputFile.is_open()) {
            for (int i = 0; i < points.size(); i++) {
                Whale whale = points[i];
                for (int j = 0; j < whale.xList.size(); j++) {
                    outputFile << whale.xList[j] << " " << whale.yList[j] << " ";
                }

                outputFile << "\n";
            }
        }
        outputFile.close();

        return 0;
    } else 
        return 0;
}   