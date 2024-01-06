path1 = "C:\Users\emmaa\Desktop\results\ab_day\test_latest\images\";
path2 = "C:\Users\emmaa\Desktop\results\ab_night\test_latest\images\";
%path3 = "C:\Users\emmaa\Desktop\results\sub5_step\test_latest\images\";

[mean1,stdev1,vals1] = get_psnr_vals(path1);
[mean2,stdev2,vals2] = get_psnr_vals(path2);
%[mean3,stdev3,vals3] = getssims(path3);

label1 = sprintf("Mean: %G StDev: %G", mean1, stdev1);
label2 = sprintf("Mean: %G StDev: %G", mean2, stdev2);
%label3 = sprintf("Mean: %G StDev: %G", mean3, stdev3);

%%
subplot(1,2,1);
histogram(vals1(:,2),15);
ylabel("Number of Occurrences")
xlabel("PSNR Score")
title("TIR to RGB Results: Day")
%xlim([0 1])
%ylim([0 1000])
legend(label1)

subplot(1,2,2);
histogram(vals2(:,2),21);
ylabel("Number of Occurrences")
xlabel("PSNR Score")
title("TIR to RGB Results: Night")
%xlim([0 1])
%ylim([0 1000])
legend(label2)

% subplot(1,3,3);
% histogram(vals3(:,2));
% xlabel("step lr policy")
% ylabel("ssim score")
% legend(label3)