"""
Copyright (C) 2019 NVIDIA Corporation.  All rights reserved.
Licensed under the CC BY-NC-SA 4.0 license (https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode).
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
import torch.nn.utils.spectral_norm as spectral_norm
# CLADE imports SPADELight here, it is the CLADE resblk name
# SEAN imports ACE here, it is the SEAN resblk name
from models.networks.normalization import SPADE, SPADELight, ACE


# ResNet block that uses SPADE.
# It differs from the ResNet block of pix2pixHD in that
# it takes in the segmentation map as input, learns the skip connection if necessary,
# and applies normalization first and then convolution.
# This architecture seemed like a standard architecture for unconditional or
# class-conditional GAN architecture using residual block.
# The code was inspired from https://github.com/LMescheder/GAN_stability.
class SPADEResnetBlock(nn.Module):
    #
    # SEAN adds optional arguments Block_Name=None, use_rgb=True,
    #
    # not sure why yet, but I add them here, because they are optional arguments
    # that are only used in ACE classes.
    def __init__(self, fin, fout, opt, Block_Name=None, use_rgb=True):
        super().__init__()

        # SEAN/ ACE-block specific attributes
        self.use_rgb = use_rgb

        self.Block_Name = Block_Name
        self.status = opt.status

        # Attributes
        self.learned_shortcut = (fin != fout)
        fmiddle = min(fin, fout)

        # create conv layers
        # There is some weird line here that is only relevant when instance maps are used.
        #
        # add_channels = 1 if (opt.norm_mode == 'clade' and not opt.no_instance) else 0

        self.conv_0 = nn.Conv2d(fin, fmiddle, kernel_size=3, padding=1)
        self.conv_1 = nn.Conv2d(fmiddle, fout, kernel_size=3, padding=1)
        if self.learned_shortcut:
            self.conv_s = nn.Conv2d(fin, fout, kernel_size=1, bias=False)

        # apply spectral norm if specified
        if 'spectral' in opt.norm_G:
            self.conv_0 = spectral_norm(self.conv_0)
            self.conv_1 = spectral_norm(self.conv_1)
            if self.learned_shortcut:
                self.conv_s = spectral_norm(self.conv_s)

        # define normalization layers
        #
        # Mike: Added the if else option of clades architecture.py
        #
        # Added the option to choose sean blocks
        spade_config_str = opt.norm_G.replace('spectral', '')
        if opt.norm_mode == 'spade':
            self.norm_0 = SPADE(spade_config_str, fin, opt.semantic_nc)
            self.norm_1 = SPADE(spade_config_str, fmiddle, opt.semantic_nc)
            if self.learned_shortcut:
                self.norm_s = SPADE(spade_config_str, fin, opt.semantic_nc)
        elif opt.norm_mode == 'clade':
            input_nc = opt.label_nc + (1 if opt.contain_dontcare_label else 0)
            self.norm_0 = SPADELight(spade_config_str, fin, input_nc, opt.no_instance, opt.add_dist)
            self.norm_1 = SPADELight(spade_config_str, fmiddle, input_nc, opt.no_instance, opt.add_dist)
            if self.learned_shortcut:
                self.norm_s = SPADELight(spade_config_str, fin, input_nc, opt.no_instance, opt.add_dist)
        elif opt.norm_mode == 'sean':
            self.use_sean = True
            our_norm_type = 'spadesyncbatch3x3'
            self.ace_0 = ACE(our_norm_type, fin, 3, ACE_Name= Block_Name + '_ACE_0', status=self.status, spade_params=[spade_config_str, fin, opt.semantic_nc], use_rgb=use_rgb)
            self.ace_1 = ACE(our_norm_type, fmiddle, 3, ACE_Name= Block_Name + '_ACE_1', status=self.status, spade_params=[spade_config_str, fmiddle, opt.semantic_nc], use_rgb=use_rgb)
            if self.learned_shortcut:
                self.ace_s = ACE(our_norm_type, fin, 3, ACE_Name= Block_Name + '_ACE_s', status=self.status, spade_params=[spade_config_str, fin, opt.semantic_nc], use_rgb=use_rgb)
        else:
            raise ValueError('%s is not a defined normalization method' % opt.norm_mode)


    # note the resnet block with SPADE also takes in |seg|,
    # the semantic segmentation map as input
    #
    # CLADE also has input_dist argument here, which we are not going to use.
    #
    # Added the SEAN specific arguments
    def forward(self, x, seg, style_codes=None, obj_dic=None):
        if not self.use_sean:
            x_s = self.shortcut(x, seg)

            dx = self.conv_0(self.actvn(self.norm_0(x, seg)))
            dx = self.conv_1(self.actvn(self.norm_1(dx, seg)))

            out = x_s + dx
        elif self.use_sean:
            x_s = self.shortcut(x, seg, style_codes, obj_dic)


            ###########  Modifications 1
            dx = self.ace_0(x, seg, style_codes, obj_dic)

            dx = self.conv_0(self.actvn(dx))

            dx = self.ace_1(dx, seg, style_codes, obj_dic)

            dx = self.conv_1(self.actvn(dx))
            ###########  Modifications 1


            out = x_s + dx

        return out

    def shortcut(self, x, seg, style_codes=None, obj_dic=None):
        if not self.use_sean:
            if self.learned_shortcut:
                x_s = self.conv_s(self.norm_s(x, seg))
            else:
                x_s = x
        elif self.use_sean:
            if self.learned_shortcut:
                x_s = self.ace_s(x, seg, style_codes, obj_dic)
                x_s = self.conv_s(x_s)

            else:
                x_s = x
        return x_s

    def actvn(self, x):
        return F.leaky_relu(x, 2e-1)


# ResNet block used in pix2pixHD
# We keep the same architecture as pix2pixHD.
class ResnetBlock(nn.Module):
    def __init__(self, dim, norm_layer, activation=nn.ReLU(False), kernel_size=3):
        super().__init__()

        pw = (kernel_size - 1) // 2
        self.conv_block = nn.Sequential(
            nn.ReflectionPad2d(pw),
            norm_layer(nn.Conv2d(dim, dim, kernel_size=kernel_size)),
            activation,
            nn.ReflectionPad2d(pw),
            norm_layer(nn.Conv2d(dim, dim, kernel_size=kernel_size))
        )

    def forward(self, x):
        y = self.conv_block(x)
        out = x + y
        return out


# VGG architecter, used for the perceptual loss using a pretrained VGG network
class VGG19(torch.nn.Module):
    def __init__(self, requires_grad=False):
        super().__init__()
        vgg_pretrained_features = torchvision.models.vgg19(pretrained=True).features
        self.slice1 = torch.nn.Sequential()
        self.slice2 = torch.nn.Sequential()
        self.slice3 = torch.nn.Sequential()
        self.slice4 = torch.nn.Sequential()
        self.slice5 = torch.nn.Sequential()
        for x in range(2):
            self.slice1.add_module(str(x), vgg_pretrained_features[x])
        for x in range(2, 7):
            self.slice2.add_module(str(x), vgg_pretrained_features[x])
        for x in range(7, 12):
            self.slice3.add_module(str(x), vgg_pretrained_features[x])
        for x in range(12, 21):
            self.slice4.add_module(str(x), vgg_pretrained_features[x])
        for x in range(21, 30):
            self.slice5.add_module(str(x), vgg_pretrained_features[x])
        if not requires_grad:
            for param in self.parameters():
                param.requires_grad = False

    def forward(self, X):
        h_relu1 = self.slice1(X)
        h_relu2 = self.slice2(h_relu1)
        h_relu3 = self.slice3(h_relu2)
        h_relu4 = self.slice4(h_relu3)
        h_relu5 = self.slice5(h_relu4)
        out = [h_relu1, h_relu2, h_relu3, h_relu4, h_relu5]
        return out

# This is the class SEAN uses to extract the style codes from the images.
class Zencoder(torch.nn.Module):
    def __init__(self, input_nc, output_nc, ngf=32, n_downsampling=2, norm_layer=nn.InstanceNorm2d):
        super(Zencoder, self).__init__()
        self.output_nc = output_nc

        model = [nn.ReflectionPad2d(1), nn.Conv2d(input_nc, ngf, kernel_size=3, padding=0),
                 norm_layer(ngf), nn.LeakyReLU(0.2, False)]
        ### downsample
        for i in range(n_downsampling):
            mult = 2**i
            model += [nn.Conv2d(ngf * mult, ngf * mult * 2, kernel_size=3, stride=2, padding=1),
                      norm_layer(ngf * mult * 2), nn.LeakyReLU(0.2, False)]

        ### upsample
        for i in range(1):
            mult = 2**(n_downsampling - i)
            model += [nn.ConvTranspose2d(ngf * mult, ngf * mult * 2, kernel_size=3, stride=2, padding=1, output_padding=1),
                       norm_layer(int(ngf * mult / 2)), nn.LeakyReLU(0.2, False)]

        model += [nn.ReflectionPad2d(1), nn.Conv2d(256, output_nc, kernel_size=3, padding=0), nn.Tanh()]
        self.model = nn.Sequential(*model)


    def forward(self, input, segmap):

        codes = self.model(input)

        segmap = F.interpolate(segmap, size=codes.size()[2:], mode='nearest')

        # print(segmap.shape)
        # print(codes.shape)


        b_size = codes.shape[0]
        # h_size = codes.shape[2]
        # w_size = codes.shape[3]
        f_size = codes.shape[1]

        s_size = segmap.shape[1]

        codes_vector = torch.zeros((b_size, s_size, f_size), dtype=codes.dtype, device=codes.device)


        for i in range(b_size):
            for j in range(s_size):
                component_mask_area = torch.sum(segmap.bool()[i, j])

                if component_mask_area > 0:
                    codes_component_feature = codes[i].masked_select(segmap.bool()[i, j]).reshape(f_size,  component_mask_area).mean(1)
                    codes_vector[i][j] = codes_component_feature

                    # codes_avg[i].masked_scatter_(segmap.bool()[i, j], codes_component_mu)

        return codes_vector
