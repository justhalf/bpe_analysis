# -*- coding: utf-8 -*-
"""
11 Apr 2019
Run BPE experiments
"""

# Import statements
from __future__ import print_function, division
import sys
import sentencepiece as spm
from argparse import ArgumentParser
import os

def encode_as_pieces(sp, in_path, out_path, append=False,
                     lowercase=False, no_space=False):
    if append:
        mode = 'a'
    else:
        mode = 'w'
    with open(in_path, 'r') as infile:
        with open(out_path, mode) as outfile:
            for line in infile:
                text = line.rstrip('\n')
                if lowercase:
                    text = text.lower()
                if no_space:
                    text = text.replace(' ', '_')
                pieces = sp.EncodeAsPieces(text)
                outfile.write('{}\n'.format(' '.join(pieces)))

def get_inpath(args, lowercase=False, no_space=False):
    outpath = args.output_files[0]
    with open(outpath, 'w') as outfile:
        for input_file in args.input_files:
            with open(input_file, 'r') as infile:
                for line in infile:
                    if line.startswith('# text = '):
                        text = line[len('# text = '):]
                        continue
                    elif line.startswith('# ToDoOrigText = '):
                        text = line[len('# ToDoOrigText = '):]
                    elif line.strip() == '':
                        if lowercase:
                            text = text.lower()
                        if no_space:
                            text = text.replace(' ', '_')
                        outfile.write(text)
    return outpath

def main():
    parser = ArgumentParser(description='Run BPE experiments')
    parser.add_argument('--mode', choices=['train', 'test'], required=True,
                        help='Whether to train or test')
    parser.add_argument('--input_files', nargs='+',
                        help='The list of input files to train on or to test on')
    parser.add_argument('--output_files', nargs='+',
                        help=('The (list of) output files to print the BPE segmentation result. '
                              'Should have either a single path or the same number of paths as the '
                              'number of input paths. For train mode, this file will be the '
                              'concatenation of the input paths.'))
    parser.add_argument('--model_prefix',
                        help='The path to model to save (train) or load (test), without extension')
    parser.add_argument('--vocab_size', type=int,
                        help='The vocab size for BPE (only applicable for train)')
    parser.add_argument('--lowercase', action='store_true',
                        help='lower case tokens')
    parser.add_argument('--no-space', action='store_true',
                        help='replace spaces with underscores')
    args = parser.parse_args()
    if args.mode == 'train':
        inpath = get_inpath(args, lowercase=args.lowercase, no_space=args.no_space)
        spm.SentencePieceTrainer.Train(('--input={} --model_prefix={} --vocab_size={} '
                                        '--model_type=bpe --split_by_whitespace=0'
                                        ).format(inpath, args.model_prefix,
                                                                   args.vocab_size))
    elif args.mode == 'test':
        sp = spm.SentencePieceProcessor()
        sp.Load('{}.model'.format(args.model_prefix))
        in_paths = args.input_files
        append = False
        if len(args.output_files) == 1:
            out_paths = [args.output_files[0]] * len(in_paths)
            append = True
        elif len(args.output_files) == len(in_paths):
            out_paths = args.output_files
        else:
            raise ValueError(('Number of files in output_files ({}) should be 1 or same as '
                              'input_files ({})').format(len(args.output_files), len(in_paths)))
        for in_path, out_path in zip(in_paths, out_paths):
            encode_as_pieces(sp, in_path, out_path, append=append,
                             lowercase=args.lowercase, no_space=args.no_space)

if __name__ == '__main__':
    main()

