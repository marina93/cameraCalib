#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 12 20:26:22 2018

@author: marina
"""
"""
This class implements Planar Calibration and RANSAC algorithms.
It uses the feature files generated in featureExtraction.py
When running the application a menu pops up in the terminal and allows the user to choose between either method.
"""
import numpy as np
import random
import sys

"""
Main method. Executes the  function according to the user input.
"""
def main():
      global imgMod, imgOrg
      print("Author: Marina Torres \n")
      while(True):
          inp = raw_input("Select a function, press 'h' to see options: ")
          print ("\n")
          if(inp == "q"):
              sys.exit(0)
          elif(inp == "h"):
              help()
          else:
              if(inp=="c"):
                  planarCalib("features.txt","features0.txt","features1.txt","features2.txt")
              elif(inp=="r"):
                  ransac("features.txt","features0.txt","features1.txt","features2.txt")
      

""" 
This function takes as input 4 text files and returns a numpy array with the data of each file.
"""      
def extractPoints(f, file0, file1, file2):
    
    objp = np.empty((0,3))
    imgpoints0 = np.empty((0,2))
    imgpoints1 = np.empty((0,2))
    imgpoints2 = np.empty((0,2))
    
    with open("../files/"+f) as f:
        for line in f:
            line = line.replace('\n',"")
            line = line.replace(' '," ")
            l = []*3
            l.append(float(line.split(" ")[0]))
            l.append(float(line.split(" ")[1]))
            l.append(float(line.split(" ")[2]))
            objp=np.append(objp,[l],axis=0)
    f.close()
    
    with open("../files/"+file0) as file0:
        for line in file0:
            line = line.replace('\n',"")
            l = []*2
            l.append(float(line.split(" ")[0]))
            l.append(float(line.split(" ")[1]))
            imgpoints0=np.append(imgpoints0,[l],axis=0)
    file0.close()
       
    with open("../files/"+file1) as file1:
        for line in file1:
            line = line.replace('\n',"")
            l = []*2 
            l.append(float(line.split(" ")[0]))
            l.append(float(line.split(" ")[1]))
            imgpoints1=np.append(imgpoints1,[l],axis=0) 
    file1.close()
        
    with open("../files/"+file2) as file2:
        for line in file2:
            line = line.replace('\n',"")
            l = []*2
            l.append(float(line.split(" ")[0]))
            l.append(float(line.split(" ")[1]))
            imgpoints2=np.append(imgpoints2,[l],axis=0)   
    file2.close()
    return objp, imgpoints0, imgpoints1, imgpoints2

"""
This function takes as input an array of 3 dimensions.
Concatenates a vector of '1' to the 3D np array to convert it to 3DH
Returns an array formed by stacking the vector and the input array.
"""
def to3DH(objp):
    objp = np.array(objp)
    n,m = objp.shape
    X0 = np.ones((n,1))
    objp2 = np.hstack((objp,X0))
    return objp2
    
"""
Implementation of planar calibration.
This function takes four files as inputs, one contains the data corresponding to the object points, and the other three are
data from the image points. The function calculates the homography matrixes between the object points and each of the image points.
It extracts the intrinsic parameters from the vector computed with the homography estimations, as well as the extrinsic parameters 
for each of the homography estimations and prints it in the terminal.
"""
def planarCalib(f, file0, file1, file2):
    
    objp, imgpoints0, imgpoints1, imgpoints2 = extractPoints(f,file0,file1,file2)
    nPoints0 = len(imgpoints0)
    nPoints1 = len(imgpoints1)
    nPoints2 = len(imgpoints2)
    H0= homogEstim(imgpoints0, objp)
    H1= homogEstim(imgpoints1, objp)
    H2= homogEstim(imgpoints2, objp)
  
    v = computeVector(H0,H1,H2)
    
    alpha,beta,gamma,u0,v0,K = intrParam(v)
    
    R0,T0 = extrParam(K,H0)
    R1,T1 = extrParam(K,H1)
    R2,T2 = extrParam(K,H2)
    
    print ("INTRINSIC PARAMETERS")
    print("alpha: ", alpha)
    print("beta: ", beta)
    print("gamma: ", gamma)
    print("u0: ", u0)
    print("v0: ", v0)
    print ("\n")
    
    print ("EXTRINSIC PARAMETERS H0")
    print ("R: ", R0)
    print ("T: ", T0)
    print ("\n")
    
    print ("EXTRINSIC PARAMETERS H1")
    print ("R: ", R1)
    print ("T: ", T1)
    print ("\n")

    
    print ("EXTRINSIC PARAMETERS H2")
    print ("R: ", R2)
    print ("T: ", T2)
    print ("\n")
    objp2 = to3DH(objp)
    
    M0,M1,M2 = matrixM(objp,imgpoints0,imgpoints1, imgpoints2)
    mse0 = mse(objp2, imgpoints0, M0, nPoints0)
    mse1 = mse(objp2, imgpoints1, M1, nPoints1)
    mse2 = mse(objp2, imgpoints2, M2, nPoints2)
    
    print ("MSE0: ",mse0)
    print ("MSE1: ",mse1)
    print ("MSE2: ",mse2)
    print ("\n")
   
"""
This function estimates the planar homography between the image plane and the object. The homography relates the transformation between two planes.
It iterates through each element of the object points to convert from 2d to 2d homogeneous matrix and compute its transpose.
Factorizes the complex matrix obtained from the image points and object points 2dh using singular value decoposition algorithm.
Returns Vh, the nxn unitary matrix whose columns are the right-singular vectors of the matrix M.
"""
def homogEstim(imgpoints,objp):
    p2dh = []
    p2dhT = []
    matrix = np.empty((0,9))
    z = [0,0,0]
    z = np.array(z)
    z = z.T
    zT = z.transpose()
    for i in range(0, len(objp)):
       row = [objp[i][0], objp[i][1], 1] 
       p2dh.append(row)
           
    p2dh = np.array(p2dh)
    for i in range(0, len(p2dh)):
        pT = p2dh[i].T
        p2dhT.append(pT)
        
    for i in range(0, len(imgpoints)):
        pT = p2dh[i].T
        x = imgpoints[i][0]
        y = imgpoints[i][1]
        val11 = pT
        val12 = zT
        val13 = -x*pT
        
        val21 = z
        val22 = pT
        val23 = -y*pT
        
        row1 = [val11[0],val11[1],val11[2], val12[0],val12[1],val12[2], val13[0], val13[1],val13[2]]
        row2 = [val21[0],val21[1],val21[2], val22[0],val22[1],val22[2], val23[0], val23[1],val23[2]]
        matrix=np.append(matrix,[row1],axis=0)
        matrix=np.append(matrix,[row2],axis=0)
                
    U,S,Vh = np.linalg.svd(matrix)
    return Vh[np.argmin(S),:].reshape(3,3)
    
"""
Auxiliary function to compute the array composed by the three Homography vectors
"""
def computeVector(H0,H1,H2):
    matrixV = []
    v0 = computeV(H0,0,1) 
    v1 = computeV(H0,0,0) - computeV(H0,1,1)
    v2 = computeV(H1,0,1) 
    v3 = computeV(H1,0,0) - computeV(H1,1,1)
    v4 = computeV(H2,0,1)
    v5 = computeV(H2,0,0) - computeV(H2,1,1)
    matrixV =np.array([v0,v1,v2,v3,v4,v5])

    return matrixV


def computeV(H,i,j):
    H = H.T
    V = np.array([H[i,0]*H[j,0], 
                  H[i,0]*H[j,1]+H[i,1]*H[j,0],
                  H[i,1]*H[j,1],
                  H[i,2]*H[j,0]+H[i,0]*H[j,2],
                  H[i,2]*H[j,1]+H[i,1]*H[j,2],
                  H[i,2]*H[j,2]])
    
    return V

"""
Auxiliary function to calculate the intrinsic parameters of the vector received as input. 
The input should be a vector composed by the three homography vectors from the three image points respectively
"""
def intrParam(v):
    U,S,Vh = np.linalg.svd(v) 
    s = Vh[np.argmin(S),:]
    
    c1 = s[1]*s[3]-s[0]*s[4]
    c2 = s[0]*s[2]-s[1]*s[1]
    v0 = c1/c2
    l = s[5]-((np.square(s[3]) + (v0*c1))/s[0])
    
    alpha = np.sqrt(l/s[0])
    
    beta = np.sqrt(l*s[0]/c2)
    gamma = -s[1]*alpha*alpha*beta/l
    
    u0 = (gamma*v0/alpha)-(s[3]*alpha*alpha/l)
    
    K = np.array([[alpha, gamma, u0],
                  [0, beta, v0],
                  [0, 0, 1]])
    
    return alpha, beta, gamma, u0, v0,K

 """
 Auxiliary function to calculate the extrinsic parameters of the homography estimation received as input.
They denote the coordinate system transformations from 3D world coordinates to 3D camera coordinates
The function returns T and R, where T is the position of the origin of the world coordinate system expressed in coordinates
 of the camera-centered coordinate system, and R is the rotation matrix.
 """   
def extrParam(K, H):
    
    h0 = H[:,0]
    h1 = H[:,1] 
    h2 = H[:,2]
    
    K_inv = np.linalg.inv(K)
    
    l = 1/(np.linalg.norm(np.matmul(K_inv, h0)))
    sign = np.sign(np.matmul(K_inv, h2)[2])
    l*=sign
    r0 = l*np.matmul(K_inv, h0)
    r1 = l*np.matmul(K_inv, h1)    
    r2 = np.cross(r0,r1)
    T = l*np.matmul(K_inv,h2).reshape(3,1) 
    R = np.transpose(np.array([r0,r1,r2]))

    return R,T

"""
Auxiliary function to calculate the RANSAC model parameters of the random data received as input. 
"""
def matrixM(objp,imgpoints0,imgpoints1, imgpoints2):

    H0= homogEstim(imgpoints0, objp)
    H1= homogEstim(imgpoints1, objp)
    H2= homogEstim(imgpoints2, objp)
  
    v = computeVector(H0,H1,H2)
    matrixK = intrParam(v)[5]
    R0,T0 = extrParam(matrixK,H0)
    R1,T1 = extrParam(matrixK,H1)
    R2,T2 = extrParam(matrixK,H2)
    M0 = np.matmul(matrixK, np.append(R0, T0, axis=1))
    M1 = np.matmul(matrixK, np.append(R1, T1, axis=1))
    M2 = np.matmul(matrixK, np.append(R2, T2, axis=1))
    return M0,M1,M2

"""
Auxiliary function to compute the mean square error between object points and image points.
"""
def mse(objp, imgp, M, nPoints):

    q = np.matmul(M, np.transpose(objp))
    q[0,:] = q[0,:]/q[2,:]
    q[1,:] = q[1,:]/q[2,:]
    err = (q[0,:]-imgp[:,0])**2 + (q[1,:]-imgp[:,1])**2
    return np.sum(err)/nPoints


"""
This method computes the RANSAC algorithm on a set of data received as input. 
First selects a random subset of data from the input dataset and computes a fitting model and the corresponding model parameters.
Next checks which elements of the remaining data are consistent with the estimated model. In case it does not fit the model within 
an error threshold it will be considered an outlier, and an inlier otherwise. 
Returns the best model for each dataset and the best error.
"""  
def ransac(f, file0, file1, file2): 
    Kmax = 1000 # maximum number of iterations allowed in the algorithm
    d= 4 # number of close data points required to assert that a model fits well to data
    threshold = float(0.1) # threshold value to determine data points that are fit well by model 
    K = 0   
    n = 5  # minimum number of data points required to estimate model parameters
    p = float(0.99)
    w = 0
    objp, imgpoints0, imgpoints1, imgpoints2 = extractPoints(f, file0, file1, file2)
    bestModel0 = None
    bestModel1 = None
    bestModel2 = None
    bestErr = np.inf
      
    errors = []
    
    for i in range(0, Kmax):
        numInliers = 0
        setObj = []*n
        setImg0 = []*n 
        setImg1 = []*n
        setImg2 =[]*n
        # Select values randomly from data
        for i in range(n):
            index = random.randint(0,len(imgpoints0)-1)
            setObj.append(objp[index])
            setImg0.append(imgpoints0[index])
            setImg1.append(imgpoints1[index])
            setImg2.append(imgpoints2[index])
        setObj = np.array(setObj)
        setImg0 = np.array(setImg0)
        setImg1 = np.array(setImg1)
        setImg2 = np.array(setImg2)
        # model parameters fitted to the random data
        M0,M1,M2 = matrixM(setObj,setImg0,setImg1,setImg2)
        objp2 = to3DH(objp) 
        q0 = np.matmul(M0, np.transpose(objp2))
        q1 = np.matmul(M1, np.transpose(objp2))
        q2 = np.matmul(M2, np.transpose(objp2))
        q0[0,:] = q0[0,:]/q0[2,:]
        q0[1,:] = q0[1,:]/q0[2,:]
        q1[0,:] = q1[0,:]/q1[2,:]
        q1[1,:] = q1[1,:]/q1[2,:]
        q2[0,:] = q2[0,:]/q2[2,:]
        q2[1,:] = q2[1,:]/q2[2,:]
        err0 = (q0[0,:]-imgpoints0[:,0])**2 + (q0[1,:]-imgpoints0[:,1])**2
        err1 = (q1[0,:]-imgpoints1[:,0])**2 + (q1[1,:]-imgpoints1[:,1])**2
        err2 = (q2[0,:]-imgpoints2[:,0])**2 + (q2[1,:]-imgpoints2[:,1])**2
        # For remaining points in data, add point to inlier if its error is under the threshold and update error with every iteration.
        for j in range(0,len(err0)):
            meanErr = float((err0[j]+err1[j]+err2[j])/3)
            errors.append(meanErr)
            if meanErr < threshold:
                numInliers+=1
                np.insert(setObj,len(setObj)-1,objp[j])
                np.insert(setImg0,len(setImg0)-1,imgpoints0[j])
                np.insert(setImg1,len(setImg1)-1,imgpoints1[j])
                np.insert(setImg2,len(setImg2)-1,imgpoints2[j])
        # Accept a model if we have reached a number of inliers large enough. Updtae parameters for further iterations. 
        if (numInliers > d):
            d = numInliers
            M0,M1,M2 = matrixM(setObj,setImg0,setImg1,setImg2)
            bestModel0 = M0
            bestModel1 = M1
            bestModel2 = M2
            w = numInliers/len(imgpoints0)  
            K = np.log(1-p)/np.log(1-(w**n))
            errors.sort()
            median = np.median(errors)
            threshold = median
            bestErr = meanErr # Measure of how good the model is
            
    print("K: ",K)
    print("w: ", w)
    print("BEST ERROR: ", bestErr)
    print("BEST MODEL 0: ",bestModel0)
    print("BEST MODEL 1: ",bestModel1)
    print("BEST MODEL 2: ",bestModel2)
            
    return bestModel0, bestModel1, bestModel2 , bestErr

"""
Help function, displays the user input options.
"""     
def help():
    print("Press 'c' for planar calibration execution.")
    print("Press 'r' for RANSAC algorithm execution.")
    print("Press 'q' to quit.")        
        
if __name__ == "__main__": main()
