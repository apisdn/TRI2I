function [m,s,tab] = getssims(path)
% getssims  get mean, standard deviation, and matrix of ssim values vs file numbers for the images on a given path.
%           file must be such that path has paired images labeled
%           "*_fake_B.png" and "*_real_B.png" in it.
%
%   [m,s,tab] = getssims(path) gets mean, stdev, and table of files vs ssim vals for image pairs in path.
    fakefiles = dir(strcat(path,"\*_fake_B.png"));
    realfiles = dir(strcat(path,"\*_real_B.png"));

    len = length(fakefiles);

    ssimvals = zeros(1,len);
    numbers = zeros(1,len);

    for i=1:len
        a = imread(strcat(path,'\',fakefiles(i).name));
        b = imread(strcat(path,'\',realfiles(i).name));
    
        mum = regexp(fakefiles(i).name,'\d*','Match');
        num = str2double(mum);
    
        ssimvals(i)=ssim(a,b);
        numbers(i)=num;
    end

    m = mean(ssimvals);
    s = std(ssimvals);
    tab = [numbers' ssimvals'];
end