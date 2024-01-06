function [m,s,tab] = get_psnr_vals(path)
% get_psnr_vals gets mean, standard deviation, and matrix of psnr values vs file numbers for the images on a given path.
%           file must be such that path has images to compare labeled
%           "*_fake_B.png" and "*_real_B.png" in it.
%
%   [m,s,tab] = get_psnr_vals(path) gets mean, stdev, and table of files vs psnr vals for image pairs in path.
    fakefiles = dir(strcat(path,"\*_fake_B.png"));
    realfiles = dir(strcat(path,"\*_real_B.png"));

    len = length(fakefiles);

    psnrvals = zeros(1,len);
    numbers = zeros(1,len);

    for i=1:len
        a = imread(strcat(path,'\',fakefiles(i).name));
        b = imread(strcat(path,'\',realfiles(i).name));
    
        mum = regexp(fakefiles(i).name,'\d*','Match');
        num = str2double(mum);
    
        psnrvals(i)=psnr(a,b);
        numbers(i)=num;
    end

    m = mean(psnrvals);
    s = std(psnrvals);
    tab = [numbers' psnrvals'];
end