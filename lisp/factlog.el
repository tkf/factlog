;;; factlog.el --- File activity logger

;; Copyright (C) 2012 Takafumi Arakaki

;; Author: Takafumi Arakaki <aka.tkf at gmail.com>

;; This file is NOT part of GNU Emacs.

;; factlog.el is free software: you can redistribute it and/or modify
;; it under the terms of the GNU General Public License as published by
;; the Free Software Foundation, either version 3 of the License, or
;; (at your option) any later version.

;; factlog.el is distributed in the hope that it will be useful,
;; but WITHOUT ANY WARRANTY; without even the implied warranty of
;; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;; GNU General Public License for more details.

;; You should have received a copy of the GNU General Public License
;; along with factlog.el.
;; If not, see <http://www.gnu.org/licenses/>.

;;; Commentary:

;;

;;; Code:

(require 'recentf)
(require 'deferred)

(defgroup factlog nil
  "File activity logger."
  :group 'convenience
  :prefix "factlog:")

(defvar factlog:lisp-dir (if load-file-name
                             (file-name-directory load-file-name)
                           default-directory))

(defvar factlog:source-dir (file-name-nondirectory factlog:lisp-dir))

(defvar factlog:cli-script
  (convert-standard-filename
   (expand-file-name "factlog/cli.py" factlog:source-dir))
  "Full path to FactLog CLI script.")

(defcustom factlog:command
  (list "python" factlog:cli-script)
  :group 'factlog)

(defun factlog:deferred-process (&rest args)
  (apply #'deferred:process factlog:command args))

(defun factlog:after-save-handler ()
  (when (recentf-include-p buffer-file-name)
    (factlog:deferred-process
     "record" "--file-point" (point) buffer-file-name)))

(provide 'factlog)

;;; factlog.el ends here
