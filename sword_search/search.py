#!/usr/bin/env python
# vim: sw=4:ts=4:sts=4:fdm=indent:fdl=0:
# -*- coding: UTF8 -*-
#
# A sword KJV indexed search module.
# Copyright (C) 2012 Josiah Gordon <josiahg@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

copying_str = \
'''
                        GNU GENERAL PUBLIC LICENSE
                           Version 3, 29 June 2007

     Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>
     Everyone is permitted to copy and distribute verbatim copies
     of this license document, but changing it is not allowed.

                                Preamble

      The GNU General Public License is a free, copyleft license for
    software and other kinds of works.

      The licenses for most software and other practical works are designed
    to take away your freedom to share and change the works.  By contrast,
    the GNU General Public License is intended to guarantee your freedom to
    share and change all versions of a program--to make sure it remains free
    software for all its users.  We, the Free Software Foundation, use the
    GNU General Public License for most of our software; it applies also to
    any other work released this way by its authors.  You can apply it to
    your programs, too.

      When we speak of free software, we are referring to freedom, not
    price.  Our General Public Licenses are designed to make sure that you
    have the freedom to distribute copies of free software (and charge for
    them if you wish), that you receive source code or can get it if you
    want it, that you can change the software or use pieces of it in new
    free programs, and that you know you can do these things.

      To protect your rights, we need to prevent others from denying you
    these rights or asking you to surrender the rights.  Therefore, you have
    certain responsibilities if you distribute copies of the software, or if
    you modify it: responsibilities to respect the freedom of others.

      For example, if you distribute copies of such a program, whether
    gratis or for a fee, you must pass on to the recipients the same
    freedoms that you received.  You must make sure that they, too, receive
    or can get the source code.  And you must show them these terms so they
    know their rights.

      Developers that use the GNU GPL protect your rights with two steps:
    (1) assert copyright on the software, and (2) offer you this License
    giving you legal permission to copy, distribute and/or modify it.

      For the developers' and authors' protection, the GPL clearly explains
    that there is no warranty for this free software.  For both users' and
    authors' sake, the GPL requires that modified versions be marked as
    changed, so that their problems will not be attributed erroneously to
    authors of previous versions.

      Some devices are designed to deny users access to install or run
    modified versions of the software inside them, although the manufacturer
    can do so.  This is fundamentally incompatible with the aim of
    protecting users' freedom to change the software.  The systematic
    pattern of such abuse occurs in the area of products for individuals to
    use, which is precisely where it is most unacceptable.  Therefore, we
    have designed this version of the GPL to prohibit the practice for those
    products.  If such problems arise substantially in other domains, we
    stand ready to extend this provision to those domains in future versions
    of the GPL, as needed to protect the freedom of users.

      Finally, every program is threatened constantly by software patents.
    States should not allow patents to restrict development and use of
    software on general-purpose computers, but in those that do, we wish to
    avoid the special danger that patents applied to a free program could
    make it effectively proprietary.  To prevent this, the GPL assures that
    patents cannot be used to render the program non-free.

      The precise terms and conditions for copying, distribution and
    modification follow.

                           TERMS AND CONDITIONS

      0. Definitions.

      "This License" refers to version 3 of the GNU General Public License.

      "Copyright" also means copyright-like laws that apply to other kinds of
    works, such as semiconductor masks.

      "The Program" refers to any copyrightable work licensed under this
    License.  Each licensee is addressed as "you".  "Licensees" and
    "recipients" may be individuals or organizations.

      To "modify" a work means to copy from or adapt all or part of the work
    in a fashion requiring copyright permission, other than the making of an
    exact copy.  The resulting work is called a "modified version" of the
    earlier work or a work "based on" the earlier work.

      A "covered work" means either the unmodified Program or a work based
    on the Program.

      To "propagate" a work means to do anything with it that, without
    permission, would make you directly or secondarily liable for
    infringement under applicable copyright law, except executing it on a
    computer or modifying a private copy.  Propagation includes copying,
    distribution (with or without modification), making available to the
    public, and in some countries other activities as well.

      To "convey" a work means any kind of propagation that enables other
    parties to make or receive copies.  Mere interaction with a user through
    a computer network, with no transfer of a copy, is not conveying.

      An interactive user interface displays "Appropriate Legal Notices"
    to the extent that it includes a convenient and prominently visible
    feature that (1) displays an appropriate copyright notice, and (2)
    tells the user that there is no warranty for the work (except to the
    extent that warranties are provided), that licensees may convey the
    work under this License, and how to view a copy of this License.  If
    the interface presents a list of user commands or options, such as a
    menu, a prominent item in the list meets this criterion.

      1. Source Code.

      The "source code" for a work means the preferred form of the work
    for making modifications to it.  "Object code" means any non-source
    form of a work.

      A "Standard Interface" means an interface that either is an official
    standard defined by a recognized standards body, or, in the case of
    interfaces specified for a particular programming language, one that
    is widely used among developers working in that language.

      The "System Libraries" of an executable work include anything, other
    than the work as a whole, that (a) is included in the normal form of
    packaging a Major Component, but which is not part of that Major
    Component, and (b) serves only to enable use of the work with that
    Major Component, or to implement a Standard Interface for which an
    implementation is available to the public in source code form.  A
    "Major Component", in this context, means a major essential component
    (kernel, window system, and so on) of the specific operating system
    (if any) on which the executable work runs, or a compiler used to
    produce the work, or an object code interpreter used to run it.

      The "Corresponding Source" for a work in object code form means all
    the source code needed to generate, install, and (for an executable
    work) run the object code and to modify the work, including scripts to
    control those activities.  However, it does not include the work's
    System Libraries, or general-purpose tools or generally available free
    programs which are used unmodified in performing those activities but
    which are not part of the work.  For example, Corresponding Source
    includes interface definition files associated with source files for
    the work, and the source code for shared libraries and dynamically
    linked subprograms that the work is specifically designed to require,
    such as by intimate data communication or control flow between those
    subprograms and other parts of the work.

      The Corresponding Source need not include anything that users
    can regenerate automatically from other parts of the Corresponding
    Source.

      The Corresponding Source for a work in source code form is that
    same work.

      2. Basic Permissions.

      All rights granted under this License are granted for the term of
    copyright on the Program, and are irrevocable provided the stated
    conditions are met.  This License explicitly affirms your unlimited
    permission to run the unmodified Program.  The output from running a
    covered work is covered by this License only if the output, given its
    content, constitutes a covered work.  This License acknowledges your
    rights of fair use or other equivalent, as provided by copyright law.

      You may make, run and propagate covered works that you do not
    convey, without conditions so long as your license otherwise remains
    in force.  You may convey covered works to others for the sole purpose
    of having them make modifications exclusively for you, or provide you
    with facilities for running those works, provided that you comply with
    the terms of this License in conveying all material for which you do
    not control copyright.  Those thus making or running the covered works
    for you must do so exclusively on your behalf, under your direction
    and control, on terms that prohibit them from making any copies of
    your copyrighted material outside their relationship with you.

      Conveying under any other circumstances is permitted solely under
    the conditions stated below.  Sublicensing is not allowed; section 10
    makes it unnecessary.

      3. Protecting Users' Legal Rights From Anti-Circumvention Law.

      No covered work shall be deemed part of an effective technological
    measure under any applicable law fulfilling obligations under article
    11 of the WIPO copyright treaty adopted on 20 December 1996, or
    similar laws prohibiting or restricting circumvention of such
    measures.

      When you convey a covered work, you waive any legal power to forbid
    circumvention of technological measures to the extent such circumvention
    is effected by exercising rights under this License with respect to
    the covered work, and you disclaim any intention to limit operation or
    modification of the work as a means of enforcing, against the work's
    users, your or third parties' legal rights to forbid circumvention of
    technological measures.

      4. Conveying Verbatim Copies.

      You may convey verbatim copies of the Program's source code as you
    receive it, in any medium, provided that you conspicuously and
    appropriately publish on each copy an appropriate copyright notice;
    keep intact all notices stating that this License and any
    non-permissive terms added in accord with section 7 apply to the code;
    keep intact all notices of the absence of any warranty; and give all
    recipients a copy of this License along with the Program.

      You may charge any price or no price for each copy that you convey,
    and you may offer support or warranty protection for a fee.

      5. Conveying Modified Source Versions.

      You may convey a work based on the Program, or the modifications to
    produce it from the Program, in the form of source code under the
    terms of section 4, provided that you also meet all of these conditions:

        a) The work must carry prominent notices stating that you modified
        it, and giving a relevant date.

        b) The work must carry prominent notices stating that it is
        released under this License and any conditions added under section
        7.  This requirement modifies the requirement in section 4 to
        "keep intact all notices".

        c) You must license the entire work, as a whole, under this
        License to anyone who comes into possession of a copy.  This
        License will therefore apply, along with any applicable section 7
        additional terms, to the whole of the work, and all its parts,
        regardless of how they are packaged.  This License gives no
        permission to license the work in any other way, but it does not
        invalidate such permission if you have separately received it.

        d) If the work has interactive user interfaces, each must display
        Appropriate Legal Notices; however, if the Program has interactive
        interfaces that do not display Appropriate Legal Notices, your
        work need not make them do so.

      A compilation of a covered work with other separate and independent
    works, which are not by their nature extensions of the covered work,
    and which are not combined with it such as to form a larger program,
    in or on a volume of a storage or distribution medium, is called an
    "aggregate" if the compilation and its resulting copyright are not
    used to limit the access or legal rights of the compilation's users
    beyond what the individual works permit.  Inclusion of a covered work
    in an aggregate does not cause this License to apply to the other
    parts of the aggregate.

      6. Conveying Non-Source Forms.

      You may convey a covered work in object code form under the terms
    of sections 4 and 5, provided that you also convey the
    machine-readable Corresponding Source under the terms of this License,
    in one of these ways:

        a) Convey the object code in, or embodied in, a physical product
        (including a physical distribution medium), accompanied by the
        Corresponding Source fixed on a durable physical medium
        customarily used for software interchange.

        b) Convey the object code in, or embodied in, a physical product
        (including a physical distribution medium), accompanied by a
        written offer, valid for at least three years and valid for as
        long as you offer spare parts or customer support for that product
        model, to give anyone who possesses the object code either (1) a
        copy of the Corresponding Source for all the software in the
        product that is covered by this License, on a durable physical
        medium customarily used for software interchange, for a price no
        more than your reasonable cost of physically performing this
        conveying of source, or (2) access to copy the
        Corresponding Source from a network server at no charge.

        c) Convey individual copies of the object code with a copy of the
        written offer to provide the Corresponding Source.  This
        alternative is allowed only occasionally and noncommercially, and
        only if you received the object code with such an offer, in accord
        with subsection 6b.

        d) Convey the object code by offering access from a designated
        place (gratis or for a charge), and offer equivalent access to the
        Corresponding Source in the same way through the same place at no
        further charge.  You need not require recipients to copy the
        Corresponding Source along with the object code.  If the place to
        copy the object code is a network server, the Corresponding Source
        may be on a different server (operated by you or a third party)
        that supports equivalent copying facilities, provided you maintain
        clear directions next to the object code saying where to find the
        Corresponding Source.  Regardless of what server hosts the
        Corresponding Source, you remain obligated to ensure that it is
        available for as long as needed to satisfy these requirements.

        e) Convey the object code using peer-to-peer transmission, provided
        you inform other peers where the object code and Corresponding
        Source of the work are being offered to the general public at no
        charge under subsection 6d.

      A separable portion of the object code, whose source code is excluded
    from the Corresponding Source as a System Library, need not be
    included in conveying the object code work.

      A "User Product" is either (1) a "consumer product", which means any
    tangible personal property which is normally used for personal, family,
    or household purposes, or (2) anything designed or sold for incorporation
    into a dwelling.  In determining whether a product is a consumer product,
    doubtful cases shall be resolved in favor of coverage.  For a particular
    product received by a particular user, "normally used" refers to a
    typical or common use of that class of product, regardless of the status
    of the particular user or of the way in which the particular user
    actually uses, or expects or is expected to use, the product.  A product
    is a consumer product regardless of whether the product has substantial
    commercial, industrial or non-consumer uses, unless such uses represent
    the only significant mode of use of the product.

      "Installation Information" for a User Product means any methods,
    procedures, authorization keys, or other information required to install
    and execute modified versions of a covered work in that User Product from
    a modified version of its Corresponding Source.  The information must
    suffice to ensure that the continued functioning of the modified object
    code is in no case prevented or interfered with solely because
    modification has been made.

      If you convey an object code work under this section in, or with, or
    specifically for use in, a User Product, and the conveying occurs as
    part of a transaction in which the right of possession and use of the
    User Product is transferred to the recipient in perpetuity or for a
    fixed term (regardless of how the transaction is characterized), the
    Corresponding Source conveyed under this section must be accompanied
    by the Installation Information.  But this requirement does not apply
    if neither you nor any third party retains the ability to install
    modified object code on the User Product (for example, the work has
    been installed in ROM).

      The requirement to provide Installation Information does not include a
    requirement to continue to provide support service, warranty, or updates
    for a work that has been modified or installed by the recipient, or for
    the User Product in which it has been modified or installed.  Access to a
    network may be denied when the modification itself materially and
    adversely affects the operation of the network or violates the rules and
    protocols for communication across the network.

      Corresponding Source conveyed, and Installation Information provided,
    in accord with this section must be in a format that is publicly
    documented (and with an implementation available to the public in
    source code form), and must require no special password or key for
    unpacking, reading or copying.

      7. Additional Terms.

      "Additional permissions" are terms that supplement the terms of this
    License by making exceptions from one or more of its conditions.
    Additional permissions that are applicable to the entire Program shall
    be treated as though they were included in this License, to the extent
    that they are valid under applicable law.  If additional permissions
    apply only to part of the Program, that part may be used separately
    under those permissions, but the entire Program remains governed by
    this License without regard to the additional permissions.

      When you convey a copy of a covered work, you may at your option
    remove any additional permissions from that copy, or from any part of
    it.  (Additional permissions may be written to require their own
    removal in certain cases when you modify the work.)  You may place
    additional permissions on material, added by you to a covered work,
    for which you have or can give appropriate copyright permission.

      Notwithstanding any other provision of this License, for material you
    add to a covered work, you may (if authorized by the copyright holders of
    that material) supplement the terms of this License with terms:

        a) Disclaiming warranty or limiting liability differently from the
        terms of sections 15 and 16 of this License; or

        b) Requiring preservation of specified reasonable legal notices or
        author attributions in that material or in the Appropriate Legal
        Notices displayed by works containing it; or

        c) Prohibiting misrepresentation of the origin of that material, or
        requiring that modified versions of such material be marked in
        reasonable ways as different from the original version; or

        d) Limiting the use for publicity purposes of names of licensors or
        authors of the material; or

        e) Declining to grant rights under trademark law for use of some
        trade names, trademarks, or service marks; or

        f) Requiring indemnification of licensors and authors of that
        material by anyone who conveys the material (or modified versions of
        it) with contractual assumptions of liability to the recipient, for
        any liability that these contractual assumptions directly impose on
        those licensors and authors.

      All other non-permissive additional terms are considered "further
    restrictions" within the meaning of section 10.  If the Program as you
    received it, or any part of it, contains a notice stating that it is
    governed by this License along with a term that is a further
    restriction, you may remove that term.  If a license document contains
    a further restriction but permits relicensing or conveying under this
    License, you may add to a covered work material governed by the terms
    of that license document, provided that the further restriction does
    not survive such relicensing or conveying.

      If you add terms to a covered work in accord with this section, you
    must place, in the relevant source files, a statement of the
    additional terms that apply to those files, or a notice indicating
    where to find the applicable terms.

      Additional terms, permissive or non-permissive, may be stated in the
    form of a separately written license, or stated as exceptions;
    the above requirements apply either way.

      8. Termination.

      You may not propagate or modify a covered work except as expressly
    provided under this License.  Any attempt otherwise to propagate or
    modify it is void, and will automatically terminate your rights under
    this License (including any patent licenses granted under the third
    paragraph of section 11).

      However, if you cease all violation of this License, then your
    license from a particular copyright holder is reinstated (a)
    provisionally, unless and until the copyright holder explicitly and
    finally terminates your license, and (b) permanently, if the copyright
    holder fails to notify you of the violation by some reasonable means
    prior to 60 days after the cessation.

      Moreover, your license from a particular copyright holder is
    reinstated permanently if the copyright holder notifies you of the
    violation by some reasonable means, this is the first time you have
    received notice of violation of this License (for any work) from that
    copyright holder, and you cure the violation prior to 30 days after
    your receipt of the notice.

      Termination of your rights under this section does not terminate the
    licenses of parties who have received copies or rights from you under
    this License.  If your rights have been terminated and not permanently
    reinstated, you do not qualify to receive new licenses for the same
    material under section 10.

      9. Acceptance Not Required for Having Copies.

      You are not required to accept this License in order to receive or
    run a copy of the Program.  Ancillary propagation of a covered work
    occurring solely as a consequence of using peer-to-peer transmission
    to receive a copy likewise does not require acceptance.  However,
    nothing other than this License grants you permission to propagate or
    modify any covered work.  These actions infringe copyright if you do
    not accept this License.  Therefore, by modifying or propagating a
    covered work, you indicate your acceptance of this License to do so.

      10. Automatic Licensing of Downstream Recipients.

      Each time you convey a covered work, the recipient automatically
    receives a license from the original licensors, to run, modify and
    propagate that work, subject to this License.  You are not responsible
    for enforcing compliance by third parties with this License.

      An "entity transaction" is a transaction transferring control of an
    organization, or substantially all assets of one, or subdividing an
    organization, or merging organizations.  If propagation of a covered
    work results from an entity transaction, each party to that
    transaction who receives a copy of the work also receives whatever
    licenses to the work the party's predecessor in interest had or could
    give under the previous paragraph, plus a right to possession of the
    Corresponding Source of the work from the predecessor in interest, if
    the predecessor has it or can get it with reasonable efforts.

      You may not impose any further restrictions on the exercise of the
    rights granted or affirmed under this License.  For example, you may
    not impose a license fee, royalty, or other charge for exercise of
    rights granted under this License, and you may not initiate litigation
    (including a cross-claim or counterclaim in a lawsuit) alleging that
    any patent claim is infringed by making, using, selling, offering for
    sale, or importing the Program or any portion of it.

      11. Patents.

      A "contributor" is a copyright holder who authorizes use under this
    License of the Program or a work on which the Program is based.  The
    work thus licensed is called the contributor's "contributor version".

      A contributor's "essential patent claims" are all patent claims
    owned or controlled by the contributor, whether already acquired or
    hereafter acquired, that would be infringed by some manner, permitted
    by this License, of making, using, or selling its contributor version,
    but do not include claims that would be infringed only as a
    consequence of further modification of the contributor version.  For
    purposes of this definition, "control" includes the right to grant
    patent sublicenses in a manner consistent with the requirements of
    this License.

      Each contributor grants you a non-exclusive, worldwide, royalty-free
    patent license under the contributor's essential patent claims, to
    make, use, sell, offer for sale, import and otherwise run, modify and
    propagate the contents of its contributor version.

      In the following three paragraphs, a "patent license" is any express
    agreement or commitment, however denominated, not to enforce a patent
    (such as an express permission to practice a patent or covenant not to
    sue for patent infringement).  To "grant" such a patent license to a
    party means to make such an agreement or commitment not to enforce a
    patent against the party.

      If you convey a covered work, knowingly relying on a patent license,
    and the Corresponding Source of the work is not available for anyone
    to copy, free of charge and under the terms of this License, through a
    publicly available network server or other readily accessible means,
    then you must either (1) cause the Corresponding Source to be so
    available, or (2) arrange to deprive yourself of the benefit of the
    patent license for this particular work, or (3) arrange, in a manner
    consistent with the requirements of this License, to extend the patent
    license to downstream recipients.  "Knowingly relying" means you have
    actual knowledge that, but for the patent license, your conveying the
    covered work in a country, or your recipient's use of the covered work
    in a country, would infringe one or more identifiable patents in that
    country that you have reason to believe are valid.

      If, pursuant to or in connection with a single transaction or
    arrangement, you convey, or propagate by procuring conveyance of, a
    covered work, and grant a patent license to some of the parties
    receiving the covered work authorizing them to use, propagate, modify
    or convey a specific copy of the covered work, then the patent license
    you grant is automatically extended to all recipients of the covered
    work and works based on it.

      A patent license is "discriminatory" if it does not include within
    the scope of its coverage, prohibits the exercise of, or is
    conditioned on the non-exercise of one or more of the rights that are
    specifically granted under this License.  You may not convey a covered
    work if you are a party to an arrangement with a third party that is
    in the business of distributing software, under which you make payment
    to the third party based on the extent of your activity of conveying
    the work, and under which the third party grants, to any of the
    parties who would receive the covered work from you, a discriminatory
    patent license (a) in connection with copies of the covered work
    conveyed by you (or copies made from those copies), or (b) primarily
    for and in connection with specific products or compilations that
    contain the covered work, unless you entered into that arrangement,
    or that patent license was granted, prior to 28 March 2007.

      Nothing in this License shall be construed as excluding or limiting
    any implied license or other defenses to infringement that may
    otherwise be available to you under applicable patent law.

      12. No Surrender of Others' Freedom.

      If conditions are imposed on you (whether by court order, agreement or
    otherwise) that contradict the conditions of this License, they do not
    excuse you from the conditions of this License.  If you cannot convey a
    covered work so as to satisfy simultaneously your obligations under this
    License and any other pertinent obligations, then as a consequence you may
    not convey it at all.  For example, if you agree to terms that obligate you
    to collect a royalty for further conveying from those to whom you convey
    the Program, the only way you could satisfy both those terms and this
    License would be to refrain entirely from conveying the Program.

      13. Use with the GNU Affero General Public License.

      Notwithstanding any other provision of this License, you have
    permission to link or combine any covered work with a work licensed
    under version 3 of the GNU Affero General Public License into a single
    combined work, and to convey the resulting work.  The terms of this
    License will continue to apply to the part which is the covered work,
    but the special requirements of the GNU Affero General Public License,
    section 13, concerning interaction through a network will apply to the
    combination as such.

      14. Revised Versions of this License.

      The Free Software Foundation may publish revised and/or new versions of
    the GNU General Public License from time to time.  Such new versions will
    be similar in spirit to the present version, but may differ in detail to
    address new problems or concerns.

      Each version is given a distinguishing version number.  If the
    Program specifies that a certain numbered version of the GNU General
    Public License "or any later version" applies to it, you have the
    option of following the terms and conditions either of that numbered
    version or of any later version published by the Free Software
    Foundation.  If the Program does not specify a version number of the
    GNU General Public License, you may choose any version ever published
    by the Free Software Foundation.

      If the Program specifies that a proxy can decide which future
    versions of the GNU General Public License can be used, that proxy's
    public statement of acceptance of a version permanently authorizes you
    to choose that version for the Program.

      Later license versions may give you additional or different
    permissions.  However, no additional obligations are imposed on any
    author or copyright holder as a result of your choosing to follow a
    later version.
'''
warranty_str = \
'''
      15. Disclaimer of Warranty.

      THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
    APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
    HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY
    OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,
    THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
    PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM
    IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF
    ALL NECESSARY SERVICING, REPAIR OR CORRECTION.

      16. Limitation of Liability.

      IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING
    WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MODIFIES AND/OR CONVEYS
    THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY
    GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE
    USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO LOSS OF
    DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD
    PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS),
    EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF
    SUCH DAMAGES.

      17. Interpretation of Sections 15 and 16.

      If the disclaimer of warranty and limitation of liability provided
    above cannot be given local legal effect according to their terms,
    reviewing courts shall apply local law that most closely approximates
    an absolute waiver of all civil liability in connection with the
    Program, unless a warranty or assumption of liability accompanies a
    copy of the Program in return for a fee.
'''

""" KJV indexer and search modules.

BibleSearch:  Can index and search the 'KJV' sword module using different types
of searches, including the following:
    Strongs number search       -   Searches for all verses containing either
                                    the phrase strongs phrase, any strongs
                                    number or a superset of the strongs
                                    numbers.
    Morphological tags search   -   Same as the strongs...
    Word or phrase search       -   Same as the strongs...
    Regular expression search   -   Searches the whole Bible using the provided
                                    regular expression.

"""

from sys import argv, exit
from cmd import Cmd
from difflib import get_close_matches
from functools import wraps
from time import strftime
from textwrap import fill
from collections import defaultdict
from itertools import product
import os
import sys
import json
import re

from .utils import *


try:
    from .sword_verses import *
except ImportError:
    Sword = None
    from .verses import *

COLOR_LEVEL = 3

# Highlight colors.
highlight_color = '\033[7m'
highlight_text = '%s\\1\033[m' % highlight_color
word_regx = re.compile(r'\b([\w-]+)\b')

# Strip previous color.
strip_color_regx = re.compile('\033\[[\d;]*m')


def render_raw2(verse_text, strongs=False, morph=False):
    """ Render raw verse text.

    """

    strong_regx = re.compile(r'strong:([GH]\d+)', re.I)
    morph_regx = re.compile(r'(?:Morph|robinson):([\w-]*)', re.I)
    test_regx = re.compile(r'''
                ([^<]*)
                <(?P<tag>seg|q|w|transChange|note)([^>]*)>
                ([\w\W]*?)
                </(?P=tag)>
                ([^<]*)
                ''', re.I | re.X)
    divname_regx = re.compile(r'''
                <(?:divineName)>
                ([^<]*?)
                ([\'s]*)
                </(?:divineName)>
                ''', re.I | re.X)
    div_upper = lambda m: m.group(1).upper() + m.group(2)
    marker_regx = re.compile(r'.*marker="(.)".*', re.I)
    info_print(verse_text, tag=4)

    def recurse_tag(text):
        """ Recursively parse raw verse text using regular expressions, and
        returns the correctly formatted text.

        """

        v_text = ''
        for match in test_regx.finditer(text):
            opt, tag_name, tag_attr, tag_text, punct = match.groups()
            strongs_str = ''
            morph_str = ''
            italic_str = '<i>%s</i>' if 'added' in tag_attr.lower() else '%s'
            if 'note' in tag_name.lower() or 'study' in tag_attr.lower():
                note_str = ' <n>%s</n>'
            else:
                note_str = '%s'
            if strongs and strong_regx.search(tag_attr):
                strongs_list = strong_regx.findall(tag_attr)
                strongs_str = ' <%s>' % '> <'.join(strongs_list)
            if morph and morph_regx.search(tag_attr):
                morph_list = morph_regx.findall(tag_attr)
                morph_str = ' {%s}' % '} {'.join(morph_list)

            if match.re.search(tag_text):
                temp_text = recurse_tag(tag_text) + strongs_str + morph_str
                v_text += note_str % italic_str % (temp_text)
            else:
                info_print((opt, tag_name, tag_attr, tag_text, punct), tag=4)
                opt = marker_regx.sub('<p>\\1</p> ', opt)
                tag_text = divname_regx.sub(div_upper, tag_text)
                tag_text = note_str % italic_str % tag_text
                v_text += opt + tag_text + strongs_str + morph_str
            v_text += punct

        return v_text

    return recurse_tag(verse_text)


def render_raw(verse_text, strongs=False, morph=False):
    """ Render raw verse text.

    """

    strong_regx = re.compile(r'strong:([GH]\d+)', re.I)
    morph_regx = re.compile(r'(?:Morph|robinson):([\w-]*)', re.I)
    test_regx = re.compile(r'''
                ([^<]*)
                <(?P<tag>q|w|transChange|note)([^>]*)>
                ([\w\W]*?)
                </(?P=tag)>
                ([^<]*)
                ''', re.I | re.X)
    divname_regx = re.compile(r'''
                (?:<seg>)?
                <(?:divineName)>+
                ([^<]*?)
                ([\'s]*)
                </(?:divineName)>
                (?:</seg>)?
                ''', re.I | re.X)
    xadded_regx = re.compile(r'<seg subType="x-added"[^>]*>([^<]*)</seg>',
                             re.I)
    div_upper = lambda m: m.group(1).upper() + m.group(2)
    marker_regx = re.compile(r'.*marker="(.)".*', re.I)
    v_text = ''
    info_print(verse_text, tag=4)

    for match in test_regx.finditer(verse_text):
        opt, tag_name, tag_attr, tag_text, punct = match.groups()
        italic_str = '%s'
        if match.re.search(tag_text):
            if 'added' in tag_attr.lower():
                italic_str = '<i>%s</i>' + punct
                punct = ''
            match_list = match.re.findall(tag_text + punct)
        else:
            match_list = [match.groups()]
        temp_text = ''
        for opt, tag_name, tag_attr, tag_text, punct in match_list:
            info_print((opt, tag_name, tag_attr, tag_text, punct), tag=4)
            tag_text = divname_regx.sub(div_upper, tag_text)
            tag_text = xadded_regx.sub('<i>\\1</i>', tag_text)
            if 'marker' in opt.lower():
                temp_text += '<p>%s</p> ' % marker_regx.sub('\\1', opt)
                opt = ''
            if 'note' in tag_name.lower() or 'study' in tag_attr.lower():
                temp_text += ' <n>%s</n>' % tag_text
                tag_text = ''
            temp_italic = '<i>%s</i>' if 'added' in tag_attr.lower() else '%s'
            temp_text += temp_italic % (opt + tag_text)
            if tag_name.strip().lower() in ['transchange', 'w', 'seg']:
                if strong_regx.search(tag_attr) and strongs:
                    temp_text += \
                            ' <%s>' % '> <'.join(strong_regx.findall(tag_attr))
                if morph_regx.search(tag_attr) and morph:
                    temp_text += \
                            ' {%s}' % '} {'.join(morph_regx.findall(tag_attr))
            temp_text += punct

        v_text += italic_str % temp_text

        continue
        opt, tag_name, tag_attr, tag_text, punct = match.groups()
        tag_text = divname_regx.sub(
                lambda m: m.group(1).upper() + m.group(2), tag_text)
        if 'marker' in opt.lower():
            v_text += '<p>%s</p> ' % marker_regx.sub('\\1', opt)
        if 'added' in tag_attr.lower():
            v_text += '<i>'
        elif 'note' in tag_name.lower() or 'study' in tag_attr.lower():
            v_text += ' <n>%s</n>' % tag_text
        if match.re.search(tag_text):
            for i in match.re.finditer(tag_text):
                info_print(i.groups(), tag=4)
                o, t_n, t_a, t_t, p = i.groups()
                if t_n.strip().lower() in ['transchange', 'w']:
                    v_text += o + t_t
                    if strong_regx.search(t_a) and strongs:
                        v_text += \
                                ' <%s>' % '> <'.join(strong_regx.findall(t_a))
                    if morph_regx.search(t_a) and morph:
                        v_text += \
                                ' {%s}' % '} {'.join(morph_regx.findall(t_a))
                v_text += p
        else:
            if tag_name.strip().lower() in ['transchange', 'w']:
                v_text += tag_text
                if strong_regx.search(tag_attr) and strongs:
                    v_text += \
                            ' <%s>' % '> <'.join(strong_regx.findall(tag_attr))
                if morph_regx.search(tag_attr) and morph:
                    v_text += \
                            ' {%s}' % '} {'.join(morph_regx.findall(tag_attr))
        if 'added' in tag_attr.lower():
            v_text += '</i>'
        v_text += punct
        info_print('%s: %s: %s: %s: %s' % (opt, tag_name, tag_attr,
                                           tag_text, punct), tag=4)
    return v_text


def render_verses_with_italics(ref_list, wrap=True, strongs=False,
                               morph=False, added=True, notes=False,
                               highlight_func=None, module='KJV', *args):
    """ Renders a the verse text at verse_ref with italics highlighted.
    Returns a strong "verse_ref: verse_text"
        ref_list        -   List of references to render
        wrap            -   Whether to wrap the text.
        strongs         -   Include Strong's Numbers in the output.
        morph           -   Include Morphological Tags in the output.
        added           -   Include added text (i.e. italics) in the output.
        notes           -   Include study notes at the end of the text.
        highlight_func  -   A function to highlight anything else
                            (i.e. search terms.)
        module          -   Sword module to render from.
        *args           -   Any additional arguments to pass to
                            hightlight_func

        highlight_func should take at least three arguments, verse_text,
        strongs, and morph.

    """

    # Set the colors of different items.
    end_color = '\033[m'

    # Build replacement strings that highlight Strong's Numbers and
    # Morphological Tags.
    if COLOR_LEVEL >= 2:
        # The Strong's and Morphology matching regular expressions.
        # Match strongs numbers.
        strongs_regx = re.compile(r'''
                    <((?:\033\[[\d;]*m)*?[GH]?\d+?(?:\033\[[\d;]*m)*?)>
                    ''', re.I | re.X)
        # It needs to match with braces or it will catch all capitalized
        # word and words with '-'s in them.
        info_print("Rendering results, please wait...\n", tag=0)
        morph_regx = re.compile(r'''
                    \{((?:\033\[[\d+;]*m)*?[\w-]*?(?:\033\[[\d+;]*m)*?)\}
                    ''', re.X)
        strongs_color = '\033[36m'
        morph_color = '\033[35m'
        strongs_highlight = '<%s\\1%s>' % (strongs_color, end_color)
        morph_highlight = '{%s\\1%s}' % (morph_color, end_color)

    if COLOR_LEVEL >= 0:
        ref_color = '\033[32m'
        ref_highlight = '%s\\1%s' % (ref_color, end_color)

    if COLOR_LEVEL >= 1 and added:
        italic_color = '\033[4m'
        italic_regx = re.compile(r'<i>\s?(.*?)\s?</i>', re.S)
        italic_highlight = '%s\\1%s' % (italic_color, end_color)

    # Get the local text encoding.
    encoding = get_encoding()

    # A substitution replacement function for highlighting italics.
    def italic_color(match):
        """ Color italic text, but first remove any previous color.

        """

        # Strip any previous colors.
        match_text = strip_color_regx.sub('', match.groups()[0])
        # Color the italics.
        return word_regx.sub(italic_highlight, match_text)

    # Get an iterator over all the requested verses.
    verse_iter = IndexedVerseTextIter(iter(ref_list), strongs, morph,
                                      italic_markers=(COLOR_LEVEL >= 1),
                                      added=added, paragraph=added,
                                      notes=notes, module=module)
    if VERBOSE_LEVEL == 20:
        verse_iter = VerseTextIter(iter(ref_list), strongs, morph,
                                module=module, markup=1, #Sword.FMT_PLAIN,
                                render='render_raw')
    if VERBOSE_LEVEL >= 30:
        verse_iter = RawDict(iter(ref_list), module=module)
    for verse_ref, verse_text in verse_iter:
        if VERBOSE_LEVEL >= 30:
            len_longest_key = len(max(verse_text[1].keys(), key=len))
            for key, value in verse_text[1].items():
                print('\033[33m{0:{1}}\033[m: {2}'.format(key,
                                                          len_longest_key,
                                                          value))
            verse_text = verse_text[1]['_verse_text'][0]
        # Encode than decode the verse text to make it compatable with
        # the locale.
        verse_text = verse_text.strip().encode(encoding, 'replace')
        verse_text = verse_text.decode(encoding, 'replace')
        verse_text = '%s: %s' % (verse_ref, verse_text)
        # The text has to be word wrapped before adding any color, or else the
        # color will add to the line length and the line will wrap too soon.
        if wrap:
            verse_text = fill(verse_text, screen_size()[1],
                              break_on_hyphens=False)

        if COLOR_LEVEL >= 0:
            # Color the verse reference.
            colored_ref = word_regx.sub(ref_highlight, verse_ref)
            verse_text = re.sub(verse_ref, colored_ref, verse_text)

        if COLOR_LEVEL >= 1 and added:
            # Highlight the italic text we previously pulled out.
            verse_text = italic_regx.sub(italic_color, verse_text)

        if COLOR_LEVEL >= 2:
            # Highlight Strong's and Morphology if they are visible.
            if strongs:
                verse_text = strongs_regx.sub(strongs_highlight, verse_text)
            if morph:
                verse_text = morph_regx.sub(morph_highlight, verse_text)

        if COLOR_LEVEL >= 3:
            # Highlight the different elements.
            if highlight_func:
                verse_text = highlight_func(verse_text, *args)

        # Finally produce the formated text.
        yield verse_text


def highlight_search_terms(verse_text, regx_list, highlight_text,
                           color_tag='\033\[[\d+;]*m', *args):
    """ Highlight search terms in the verse text.

    """

    def highlight_group(match):
        """ Highlight each word/Strong's Number/Morphological Tag in the
        match.

        """

        match_text = match.group()
        for word in set(match.groups()):
            if word: # and word != match_text:
                info_print(word, tag=20)
                try:
                    match_text = re.sub('''
                            (
                            (?:{0}|\\b)+
                            {1}
                            (?:{0}|\\b)+
                            )
                            '''.format(color_tag, re.escape(word)),
                            highlight_text, match_text, flags=re.X)
                except Exception as err:
                    info_print("Error with highlighting word %s: %s" % \
                               (word, err), tag=4)
            #match_text = match_text.replace(word, '\033[7m%s\033[m' % word)
        # print(match_text)
        return match_text

        # Strip any previous colors.
        match_text = strip_color_regx.sub('', match.group())
        return word_regx.sub(highlight_text, match_text)

    verse_text = verse_text.strip()
    # Apply each highlighting regular expression to the text.
    for regx in regx_list:
        verse_text = regx.sub(highlight_group, verse_text)

    return verse_text


def build_highlight_regx(search_list, case_sensitive, sloppy=False,
                         color_tag='\033\[[\\\\d+;]*m', extra_tag='\033'):
    """ Build a regular expression and highlight string to colorize the
    items in search_list as they appear in a verse.

    """

    if not search_list:
        return []

    regx_list = []
    # Extra word boundry to catch ansi color escape sequences.
    escaped_word_bound = '(?:{0}|\\\\b)+'.format(color_tag)
    word_bound = '(?:{0}|\\b)+'.format(color_tag)
    # Extra space filler to pass over ansi color escape sequences.
    extra_space = '|{0}|{1}'.format(color_tag, extra_tag)
    # print(word_bound, extra_space, '(?:\033\[[\d+;]*m|\\b)+')
    for item in search_list:
        item = item.strip()
        is_regex = (('*' in item and ' ' not in item) or item.startswith('&'))
        if ('*' in item and ' ' not in item) and  not item.startswith('&'):
            # Build a little regular expression to highlight partial words.
            item = item[1:] if item[0] in '!^+|' else item
            item = item.replace('*', '\w*')
            item = r'{0}({1}){0}'.format(word_bound, item)
        if item.startswith('&'):
            # Just use a regular expression. ('&' marks the term as a regular
            # expression.)
            item = item[1:]

        regx_list.append(Search.search_terms_to_regex(item, case_sensitive,
                word_bound=escaped_word_bound, extra_space=extra_space,
                sloppy=(sloppy or '~' in item), is_regex=is_regex))

    return regx_list


def mod_lookup(mod, items):
    """ Looks up items in a module and returns the formated text.

    """

    item_lookup = Lookup(mod)

    # Seperate all elements by a comma.
    item_list = ','.join(items.split()).split(',')
    text_list = []
    for item in item_list:
        item_text = item_lookup.get_formatted_text(item)
        text_list.append('\033[1m%s\033[m:\n%s' % (item, item_text))
    return '\n\n'.join(text_list)


class StdoutRedirect(object):
    """ Redirect stdout to a specified output function.

    """

    def __init__(self, output_func, *args):
        """ Set the output function and get the extra arguments to pass to it.

        """

        self._output_func = output_func
        self._args = args
        self._old_stdout = sys.stdout

    def write(self, data):
        """ Write data to the output function.

        """

        if data.strip():
            self._output_func(data, *self._args)

    def __enter__(self):
        """ Change sys.stdout to this class.

        """

        try:
            sys.stdout = self
            return self
        except Exception as err:
            print("Error in __enter__: %s" % err, file=sys.stderr)
            return None

    def __exit__(self, exc_type, exc_value, traceback):
        """ Change sys.stdout back to its old value.

        """

        try:
            sys.stdout = self._old_stdout
            if exc_type:
                return False
            return True
        except Exception as err:
            print("Error in __exit__: %s" % err, file=sys.stderr)
            return False


class IndexedVerseTextIter(object):
    """ An iterable object for accessing verses in the Bible.  Maybe it will
    be easier maybe not.

    """

    def __init__(self, reference_iter, strongs=False, morph=False,
                 module='KJV', italic_markers=False, added=True,
                 paragraph=True, notes=False, path=''):
        """ Initialize.

        """

        self._fix_regx = re.compile(r'\s\s+')
        self._punc_fix_regx = re.compile(r'\s([?.!;:\',"])')

        reg_list = []
        if not strongs:
            reg_list.append(r'\s*<([GH]\d+)>')
        if not morph:
            reg_list.append(r'\s*\{([\w-]+)\}')
        if not added:
            reg_list.append(r'\s?<i>\s?(.*?)\s?</i>')
        if not italic_markers:
            reg_list.append(r'(<i>\s?|\s?</i>)')
        if not paragraph:
            reg_list.append(r'\s?<p>\s?(.*?)\s?</p>')
        else:
            reg_list.append(r'(<p>\s?|\s?</p>)')
        reg_str = r'(?:%s)' % r'|'.join(reg_list)
        self._clean_regex = re.compile(reg_str, re.S)

        self._notes_regex = re.compile(r'\s?<n>\s?(.*?)\s?</n>', re.S)
        self._notes_str = ' (Notes: \\1)' if notes else ''

        self._index_dict = IndexDict('%s' % module, path)

        self._ref_iter = reference_iter

    def next(self):
        """ Returns the next verse reference and text.

        """

        return self.__next__()

    def __next__(self):
        """ Returns a tuple of the next verse reference and text.

        """

        # Retrieve the next reference.
        verse_ref = next(self._ref_iter)

        # Set the verse and render the text.
        verse_text = self._get_text(verse_ref)

        return (verse_ref, verse_text.strip())

    def __iter__(self):
        """ Returns an iterator of self.

        """

        return self

    def _get_text(self, verse_ref):
        """ Returns the verse text.  Override this to produce formatted verse
        text.

        """

        verse_text = self._index_dict[verse_ref]
        verse_text = self._clean_regex.sub(' ', verse_text)
        verse_text = self._fix_regx.sub(' ', verse_text).strip()
        verse_text = self._punc_fix_regx.sub(r'\1', verse_text).strip()
        verse_text = self._notes_regex.sub(self._notes_str, verse_text)

        return verse_text


class CombinedParse(object):
    """ A parser for simple combined search parsing.
        ((in OR tree) AND the) AND (house OR bush) =>
        ['in the house', 'in the bush', 'tree the house', 'tree the bush']
        Also it has a NOT word list.
        created NOT (and OR but) => ['created'] ['and', 'but']

    """

    def __init__(self, arg_str):
        """ Initialize the parser and parse the arg string.

        """

        self._arg_str = arg_str
        self._arg_list = arg_str.split()
        parsed_list = self.parse_string(list(arg_str))
        self._word_list, self._not_list = self.parse_list(parsed_list)

    # Make the results accesable via read-only properties.
    word_list = property(lambda self: self._word_list)
    not_list = property(lambda self: self._not_list)

    def parse_list(self, arg_list):
        """ Parse a list such as ['created', 'NOT', ['and', 'OR', 'but']] into
        search_args = ['created'] not_list = ['and', 'but']

        """

        # The list we're working on building.
        working_list = []
        # The list of words not to include.
        not_list = []
        for i in arg_list:
            # Skip 'OR's
            if i == 'OR':
                continue
            if isinstance(i, list):
                # A list was found so parse it and get the results.
                temp_list, temp_not_list = self.parse_list(i)
                # Add the returned not list to the current not list.
                not_list.extend(temp_not_list)
                if working_list:
                    if working_list[-1] == 'AND':
                        # Pop the 'AND' off the end of the list.
                        working_list.pop()
                        # Combine each element of the working listh with each
                        # element of the returned list replace the working
                        # list with those combinations.
                        # (i.e. working_list = ['this', 'that']
                        #       temp_list = ['tree', 'house']
                        #       result = ['this tree', 'this house',
                        #                 'that tree', 'that house']
                        working_list = ['%s %s' % j \
                                for j in product(working_list, temp_list)]
                    elif working_list[-1] == 'NOT':
                        # Take the 'NOT' off to show we've processed it.
                        working_list.pop()
                        # Add the returned list to the NOT list.
                        not_list.extend(temp_list)
                    else:
                        # Just extend the working list with the retuned list.
                        working_list.extend(temp_list)
                else:
                    # Just extend the working list with the retuned list.
                    working_list.extend(temp_list)
            else:
                if i == 'AND':
                    # Put the 'AND' on the list for later processing.
                    working_list.append(i)
                elif working_list:
                    if working_list[-1] == 'AND':
                        # Take the 'AND' off the list.
                        working_list.pop()
                        # Combine all the elements of working_list with i, and
                        # replace working list with the resulting list.
                        # (i.e. working_list = ['he', 'it'] i = 'said'
                        #       result = ['he said', 'it said']
                        working_list = ['%s %s' % (j, i) for j in working_list]
                    elif working_list[-1] == 'NOT':
                        # Remove the 'NOT'.
                        working_list.pop()
                        # Add the word to the not list.
                        not_list.append(i)
                    else:
                        # Add the word to the working list.
                        working_list.append(i)
                else:
                    # Add the word to the working list.
                    working_list.append(i)

        # Split and then combine all the strings in working_list.
        # Basically removes runs of whitespace.
        working_list = [' '.join(i.split()) for i in working_list]

        # Return the final list and not list.
        return working_list, not_list

    def parse_parenthesis(self, arg_list):
        """ Recursively processes strings in parenthesis converting them
        to nested lists of strings.

        """

        # The return list.
        return_list = []
        # Temorary string.
        temp_str = ''
        while arg_list:
            # Get the next character.
            c = arg_list.pop(0)
            if c == '(':
                # An opening parenthesis was found so split the current string
                # at the spaces putting them in the return list, and clean
                # the string.
                if temp_str:
                    return_list.extend(temp_str.split())
                    temp_str = ''
                # Process from here to the closing parenthesis.
                return_list.append(self.parse_parenthesis(arg_list))
            elif c == ')':
                # The parenthesis is closed so return back to the calling
                # function.
                break
            else:
                # Append the current not parenthesis character to the string.
                temp_str += c
        if temp_str:
            # Split and add the string to the return list.
            return_list.extend(temp_str.split())
        # Return what we found.
        return return_list

    def parse_string(self, arg_list):
        """ Parse a combined search arg string.  Convert a string such as:
        'created NOT (and OR but)' => ['created', 'NOT', ['and', 'OR', 'but']]

        """

        # This does the same thing only using json.
        #
        # Regular expression to group all words.
        #word_regx = re.compile(r'\b(\w*)\b')
        # Put quotes around all words and opening replace paranthesis with
        # brackets, put all of that in brackets.
        #temp_str = '[%s]' % word_regx.sub('"\\1"', arg_str).replace('(', '[')
        # Replace closing parenthesis with brackets and replace a '" ' with
        # '", '.
        #temp_str = temp_str.replace(')', ']').replace('" ', '",')
        # finally replace '] ' with '], '.  The end result should be a valid
        # json string that can be converted to a list.
        #temp_str = temp_str.replace('] ', '],')
        # Convert the string to a list.
        #return_list = json.loads(temp_str)
        #return return_list

        # The return list.
        return_list = []
        # Temporary string.
        temp_str = ''
        while arg_list:
            # Pop the next character.
            c = arg_list.pop(0)
            if c == '(':
                # A parenthesis was found store and reset the string.
                # And parse the what is in the parenthesis.
                if temp_str:
                    return_list.extend(temp_str.split())
                    temp_str = ''
                return_list.append(self.parse_parenthesis(arg_list))
            else:
                # Append the non parenthesis character to the string.
                temp_str += c

        if temp_str:
            # Store the final string in the list.
            return_list.extend(temp_str.split())

        #info_print(return_list)
        # Return the list.
        return return_list


class Search(object):
    """ Provides a simple way of searching an IndexDict for verses.

    """

    # To check for spaces.
    _whitespace_regx = re.compile(r'\s')

    # Cleanup regular expressions.
    _non_alnum_regx = re.compile(r'[^\w\*<>\{\}\(\)-]')
    _fix_regx = re.compile(r'\s+')

    # Match strongs numbers.
    _strongs_regx = re.compile(r'[<]?(\b[GH]\d+\b)[>]?', re.I)
    # It needs to match with braces or it will catch all capitalized
    # word and words with '-'s in them.
    _morph_regx = re.compile(r'[\(\{](\b[\w-]+\b)[\}\)]', re.I)
    _word_regx = re.compile(r'\b([\w\\-]+)\b')
    _space_regx = re.compile(r'\s+')
    _non_word_regx = re.compile(r'[<>\(\)]')

    _fix_strongs = classmethod(lambda c, m: '<%s>' % m.groups()[0].upper())
    _fix_morph = classmethod(lambda c, m: '{%s}' % m.groups()[0].upper())

    # Escape the morphological tags.
    _escape_morph = classmethod(lambda c, m: \
            '\{%s\}' % re.escape(m.groups()[0]).upper())

    def __init__(self, module='KJV', path='', multiword=False):
        """ Initialize the search.

        """

        # The index dictionary.
        self._index_dict = IndexDict(module, path)

        self._module_name = module
        self._multi = multiword

    @classmethod
    def search_terms_to_regex(cls, search_terms, case_sensitive,
                              word_bound='\\\\b', extra_space='',
                              sloppy=False, is_regex=False):
        """ Build a regular expression from the search_terms to match a verse
        in the Bible.

        """

        # Set the flags for the regular expression.
        flags = re.I if not case_sensitive else 0

        if is_regex:
            reg_str = search_terms
            info_print('\nUsing regular expression: %s\n' % reg_str, tag=2)

            try:
                return re.compile(reg_str, flags)
            except Exception as err:
                print("An error occured while compiling the highlight "
                      "regular expression %s: %s." % (reg_str, err),
                      " There will be no highlighting.\n", file=sys.stderr)
                return re.compile(r'')

        # This will skip words.
        not_words_str = r'\b\w+\b'
        # This will skip Strong's Numbers.
        not_strongs_str = r'<[^>]*>'
        # This wil skip Morphological Tags.
        not_morph_str = r'\{[^\}]*\}'
        # This will skip all punctuation.  Skipping ()'s is a problem for
        # searching Morphological Tags, but it is necessary for the
        # parenthesized words.  May break highlighting.
        not_punct_str = r'[\s,\?\!\.;:\\/_\(\)\[\]"\'-]'
        # This will skip ansi color.
        not_color_str = r'\033\[[\d;]*m'
        # Match all *'s
        star_regx = re.compile(r'\*')

        # Hold the string that fills space between search terms.
        space_str = ''

        # Get stars past so we can replace them with '\w*' later.
        temp_str, word_count = star_regx.subn(r'_star_', search_terms)

        # Hack to get rid of unwanted characters.
        temp_str = cls._non_alnum_regx.sub(' ', temp_str).split()
        temp_str = ' '.join(temp_str)
        # Phrases will have spaces in them
        phrase = bool(cls._whitespace_regx.search(temp_str))
        # Escape the morphological tags, and also find how many there are.
        temp_str, morph_count = cls._morph_regx.subn(cls._escape_morph,
                                                         temp_str)
        # Make all Strong's Numbers uppercase, also find how many there are.
        temp_str, strongs_count = cls._strongs_regx.subn(cls._fix_strongs,
                                                         temp_str)
        # Select all words.
        #repl = '(\\\\b\\1\\\\b)'
        # This works:
        # temp_str, word_count = \
        #       cls._word_regx.subn('{0}(\\1){0}'.format(word_bound), temp_str)
        repl = '(?:{0}(\\1){0})'.format(word_bound)
        temp_str, word_count = cls._word_regx.subn(repl, temp_str)
        # Replace what used to be *'s with '\w*'.
        temp_str = temp_str.replace('_star_', '\w*')

        # All the Strong's and Morphology were changed in the previous
        # substitution, so if that number is greater than the number of
        # Strong's plus Morphology then there were words in the search terms.
        # I do this because I don't know how to only find words.
        words_found = (strongs_count + morph_count) < word_count
        if phrase:
            # Build the string that is inserted between the items in the
            # search string.
            space_str = r'(?:%s%s' % (not_punct_str, extra_space)
            if not bool(strongs_count) or sloppy:
                # Skip over all Strong's Numbers.
                space_str = r'%s|%s' % (space_str, not_strongs_str)
            if not bool(morph_count) or sloppy:
                # Skip all Morphological Tags.
                space_str = r'%s|%s' % (space_str, not_morph_str)
            if not words_found or bool(morph_count) or bool(strongs_count) or \
                    sloppy:
                # Skip words.  If word attributes are in the search we can
                # skip over words and still keep it a phrase.
                space_str = r'%s|%s' % (space_str, not_words_str)
            # Finally make it not greedy.
            space_str = r'%s)*?' % space_str
        else:
            space_str = ''
        # Re-combine the search terms with the regular expression string
        # between each element.
        reg_str = space_str.join(temp_str.split())
        info_print('\nUsing regular expression: %s\n' % reg_str, tag=2)

        try:
            return re.compile(reg_str, flags)
        except Exception as err:
            print("An error occured while compiling the highlight "
                  "regular expression %s: %s." % (reg_str, err),
                  " There will be no highlighting.\n", file=sys.stderr)

            return re.compile(r'')

    def _sorted_iter(self, verse_ref_set):
        """ Returns an iterator over a sorted version of verse_ref_set.

        """

        # Speed up the iteration by first sorting the range.
        return iter(sorted(verse_ref_set, key=sort_key))

    def _clean_text(self, text):
        """ Return a clean (only alphanumeric) text of the provided string.

        """

        # Do we have to use two regular expressions to do this.
        # Replace all non-alphanumeric characters with a space.
        temp_text = self._non_alnum_regx.sub(' ', text)
        # Replace one or more spaces with one space.
        clean_text = self._fix_regx.sub(' ', temp_text)

        return clean_text.strip()

    def _fix_strongs_morph(self, search_terms):
        """ Make any Strong's or Morphology uppercase, put parenthesis around
        the Morphological Tags, and put <>'s around the Strong's Numbers.

        """

        # Capitalize all strongs numbers and remove the <> from them.
        temp_str = self._strongs_regx.sub(self._fix_strongs, search_terms)
        # Capitalize all morphological tags and make sure they are in
        # parenthesis.
        temp_str = self._morph_regx.sub(self._fix_morph, temp_str)

        return temp_str

    def _process_search(func):
        """ Returns a wrapper function that processes the search terms, calls
        the wrapped function, and, if applicable, confines the resulting verse
        set to a range.

        """

        @wraps(func)
        def wrapper(self, search_terms, strongs=False, morph=False,
                    added=True, case_sensitive=False, range_str=''):
            """ Process the search terms according to the wrapped functions
            requirements, then apply the range, if given, to the returned set
            of verses.

            """

            if func.__name__ in ['sword_search']:
                if not Sword:
                    print("Sword library not found.")
                    return

            if not isinstance(search_terms, str):
                # Combine the terms for use by the different methods.
                search_terms = ' '.join(search_terms)

            # Get a valid set of verse references that conform to the passed
            # range.
            range_set = parse_verse_range(range_str)

            if func.__name__ not in ['regex_search', 'partial_word_search']:
                # Try to catch and fix any Strong's Numbers or Morphological
                # Tags.
                search_terms = self._fix_strongs_morph(search_terms)

            # Regular expression and combined searches get the search terms as
            # they were passed.
            if func.__name__ in ['multiword_search', 'anyword_search',
                                 'phrase_search', 'mixed_phrase_search']:
                # Get rid of any non-alphanumeric or '-' characters from
                # the search string.
                search_str = self._clean_text(search_terms).strip()
                if strongs or morph:
                    # Strong's numbers and Morphological tags are all
                    # uppercase.  This is only required if the Morphological
                    # Tags were not surrounded by parenthesis.
                    search_str = search_str.upper().strip()
            else:
                search_str = search_terms

            # Get the set of found verses.
            found_set = func(self, search_str, strongs, morph, added,
                             case_sensitive, range_set)

            # The phrase, regular expression, and combined searches apply the
            # range before searching, so only multi-word and any-word searches
            # have it applied here.
            if func.__name__ in ['multiword_search', 'anyword_search',
                                 'partial_word_search']:
                if range_set:
                    found_set.intersection_update(range_set)
            return found_set

        # Return wrapper function.
        return wrapper

    @_process_search
    def combined_search(self, search_terms, strongs=False, morph=False,
                        added=True, case_sensitive=False, range_str=''):
        """ combined_search(self, search_terms, strongs=False, morph=False,
                        case_sensitive=False, range_str=''): ->
        Perform a combined search.  Search terms could be
        'created NOT (and OR but)' and it would find all verses with the word
        'created' in them and remove any verse that had either 'and' or 'but.'

            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            added           -   Search in the added text (i.e. italics).
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        info_print("Searching for '%s'..." % search_terms, tag=1)

        # Process the search_terms.
        arg_parser = CombinedParse(search_terms)
        # Get the list of words and/or phrases to include.
        word_list = arg_parser.word_list
        # Get the list of words and/or phrases to NOT include.
        not_list = arg_parser.not_list

        phrase_search = self.phrase_search
        multiword_search = self.multiword_search

        def combine_proc(str_list):
            """ Performs combined search on the strings in str_list, and
            returns a set of references that match.

            """

            and_it = False
            temp_set = set()
            for word in str_list:
                # A '+' before or after a word means it should have a phrase
                # search done on it and the words with it.
                if '+' in word:
                    # Do a phrase search on the word string.
                    result_set = phrase_search(word.replace('+', ' '), strongs,
                                               morph, case_sensitive,
                                               range_str)
                elif word == '&':
                    # Combine the next search results with this one.
                    and_it = True
                    continue
                else:
                    # Do a multi-word search on the word string.
                    result_set = multiword_search(word, strongs, morph,
                                                  case_sensitive, range_str)
                if and_it:
                    # The previous word said to find verses that match both.
                    temp_set.intersection_update(result_set)
                    and_it = False
                else:
                    # Only keep the verses that have either one group or the
                    # other but not both.
                    temp_set.symmetric_difference_update(result_set)

            return temp_set

        # Remove any verses that have the NOT words in them.
        found_set = combine_proc(word_list).difference(combine_proc(not_list))

        return found_set

    @_process_search
    def combined_phrase_search(self, search_terms, strongs=False, morph=False,
                               added=True, case_sensitive=False, range_str=''):
        """ combined_phrase_search(self, search_terms, strongs=False,
                morph=False, case_sensitive=False, range_str=''): ->
        Perform a combined phrase search.  Search terms could be
        'created NOT (and AND but)' and it would find all verses with the word
        'created' in them and remove any verse that had the phrase 'and but.'

            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            added           -   Search in the added text (i.e. italics).
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        info_print("Searching for '%s'..." % search_terms, tag=1)

        # Process the search_terms.
        arg_parser = CombinedParse(search_terms)
        # Get the list of words and/or phrases to include.
        word_list = arg_parser.word_list
        # Get the list of words and/or phrases to NOT include.
        not_list = arg_parser.not_list

        phrase_search = self.phrase_search

        def combine_proc(str_list):
            """ Performs combined phrase search on the strings in str_list, and
            returns a set of references that match.

            """

            temp_set = set()
            for word in str_list:
                # Do a phrase search on the word string.
                result_set = phrase_search(word.replace('+', ' '), strongs,
                                           morph, case_sensitive,
                                           range_str)
                # Include all the verses that have any of the word groups.
                temp_set.update(result_set)

            return temp_set

        # Remove any verses that have the NOT words in them.
        found_set = combine_proc(word_list).difference(combine_proc(not_list))

        return found_set

    @_process_search
    def multiword_search(self, search_terms, strongs=False, morph=False,
                         added=True, case_sensitive=False, range_str=''):
        """ multiword_search(self, search_terms, strongs=False, morph=False,
                  case_sensitive=False, range_str='') ->
        Perform a multiword search using the search_terms.

            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            added           -   Search in the added text (i.e. italics).
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        info_print("Searching for verses with all these words "
                   "'%s'..." % ', '.join(search_terms.split()), tag=1)

        # All that needs to be done is find all references with all the
        # searched words in them.
        found_set = self._index_dict.value_intersect(search_terms.split(),
                                                     case_sensitive)

        return found_set

    @_process_search
    def eitheror_search(self, search_terms, strongs=False, morph=False,
                        added=True, case_sensitive=False, range_str=''):
        """ eitheror_search(self, search_terms, strongs=False, morph=False,
                case_sensitive=False, range_str='') ->
        Perform a search returning any verse with one and only one of the terms
        searched for.

            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            added           -   Search in the added text (i.e. italics).
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        info_print("Searching for verses with one and not all of these words "
                   "'%s'..." % ', '.join(search_terms.split()), tag=1)

        # Any verse with one and only one of the searched words.
        found_set = self._index_dict.value_sym_diff(search_terms.split(),
                                                    case_sensitive)

        return found_set

    @_process_search
    def anyword_search(self, search_terms, strongs=False, morph=False,
                       added=True, case_sensitive=False, range_str=''):
        """ anyword_search(self, search_terms, strongs=False, morph=False,
                case_sensitive=False, range_str='') ->
        Perform a search returning any verse with one or more of the search
        terms.

            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            added           -   Search in the added text (i.e. italics).
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        info_print("Searching for verses with any of these words "
                   "'%s'..." % ', '.join(search_terms.split()), tag=1)

        # Any verse with one or more of the searched words.
        found_set = self._index_dict.value_union(search_terms.split(),
                                                 case_sensitive)

        return found_set

    @_process_search
    def partial_word_search(self, search_terms, strongs=False, morph=False,
                           added=True, case_sensitive=False, range_str=''):
        """ partial_word_search(self, search_terms, strongs=False, morph=False,
                case_sensitive=False, range_str='') ->
        Perform a search returning any verse with one or more words matching
        the partial words given in the search terms.  Partial words are markes
        tih *'s (e.g. '*guil*' will match any word with 'guil' in it such as
        'guilt' or 'beguile.'

            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            added           -   Search in the added text (i.e. italics).
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        info_print("Searching for verses with any of these partial words "
                   "'%s'..." % ', '.join(search_terms.split()), tag=1)

        #found_set = self._index_dict.value_union(
                #self._words_from_partial(search_terms, case_sensitive),
                #case_sensitive)
        search_list = search_terms.split()
        found_set = self._index_dict.from_partial(search_list, case_sensitive)

        return found_set

    def _words_from_partial(self, partial_word_list, case_sensitive=False):
        """ Search through a list of partial words and yield words that match.

        """

        flags = re.I if not case_sensitive else 0

        # Split the search terms and search through each word key in the index
        # for any word that contains the partial word.
        word_list = partial_word_list.split()
        for word in self._index_dict['_words_']:
            for partial_word in word_list:
                # A Regular expression that matches any number of word
                # characters for every '*' in the term.
                reg_str = '\\b%s\\b' % partial_word.replace('*', '\w*')
                try:
                    word_regx = re.compile(reg_str, flags)
                except Exception as err:
                    print('There is a problem with the regular expression '
                          '%s: %s' % (reg_str, err), file=sys.stderr)
                    exit()
                if word_regx.match(word):
                    yield word

    def _process_phrase(func):
        """ Returns a wrapper function for wrapping phrase like searches.

        """

        @wraps(func)
        def wrapper(self, search_terms, strongs=False, morph=False,
                    added=True, case_sensitive=False, range_str=''):
            """ Gets a regular expression from the wrapped function, then
            builds a set of verse references to search, finally it calls the
            searching function with the regular expression and the verse
            reference iterator, and returns the resulting set of references.

            """

            search_regx = func(self, search_terms, strongs, morph, added,
                               case_sensitive, range_str)

            # First make sure we are only searching verses that have all the
            # search terms in them.
            search_list = search_terms.split()
            if '*' in search_terms:
                ref_set = self._index_dict.from_partial(search_list,
                                                        case_sensitive,
                                                        common_limit=5000)
            else:
                ref_set = self._index_dict.value_intersect(search_list,
                                                           case_sensitive)
            if range_str:
                # Only search through the supplied range.
                ref_set.intersection_update(range_str)

            # No need to search for a single word phrase.
            if len(search_terms.split()) == 1:
                return ref_set

            # Sort the list so it may be a little faster.  Only needed if we're
            # using the sword module to look them up.
            ref_iter = self._sorted_iter(ref_set)

            # Disable Strong's and Morphological if only words are used.
            strongs = bool(self._strongs_regx.search(search_terms))
            morph = bool(self._morph_regx.search(search_terms))

            return self.find_from_regex(ref_iter, search_regx, strongs, morph)

        return wrapper

    @_process_search
    @_process_phrase
    def ordered_multiword_search(self, search_terms, strongs=False,
                                 morph=False, added=True, case_sensitive=False,
                                 range_str=''):
        """ ordered_multiword_search(self, search_terms, strongs=False,
            morph=False, case_sensitive=False, range_str='') ->
        Perform an ordered multiword search.  Like a multiword search, but all
        the words have to be in order.

            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            added           -   Search in the added text (i.e. italics).
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        info_print("Searching for verses with these words in order "
                   "'%s'..." % search_terms, tag=1)

        return self.search_terms_to_regex(search_terms, case_sensitive,
                                          sloppy=True)

    @_process_search
    @_process_phrase
    def phrase_search(self, search_terms, strongs=False, morph=False,
                      added=True, case_sensitive=False, range_str=''):
        """ phrase_search(self, search_terms, strongs=False, morph=False,
               case_sensitive=False, range_str='') ->
        Perform a phrase search.

            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            added           -   Search in the added text (i.e. italics).
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        info_print("Searching for verses with this phrase "
                   "'%s'..." % search_terms, tag=1)

        # Make all the terms the same case if case doesn't matter.
        flags = re.I if not case_sensitive else 0

        if strongs:
            # Match strongs phrases.
            search_reg_str = search_terms.replace(' ', r'[^<]*')
        elif morph:
            # Match morphological phrases.
            search_reg_str = search_terms.replace(' ', r'[^\{]*')
        else:
            # Match word phrases
            search_reg_str = '\\b%s\\b' % search_terms.replace(' ',
                    r'\b(<[^>]*>|\{[^\}]*\}|\W)*\b')

        # Make a regular expression from the search terms.
        return re.compile(search_reg_str, flags)

    @_process_search
    @_process_phrase
    def mixed_phrase_search(self, search_terms, strongs=False, morph=False,
                            added=True, case_sensitive=False, range_str=''):
        """ mixed_phrase_search(self, search_terms, strongs=False, morph=False,
        case_sensitive=False, range_str='') ->
        Perform a phrase search.

            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            added           -   Search in the added text (i.e. italics).
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        info_print("Searching for verses with this phrase "
                   "'%s'..." % search_terms, tag=1)

        # Make a regular expression from the search terms.
        return self.search_terms_to_regex(search_terms, case_sensitive)

    @_process_search
    def regex_search(self, search_terms, strongs=False, morph=False,
                     added=True, case_sensitive=False, range_str=''):
        """ regex_search(self, search_terms, strongs=False, morph=False,
              case_sensitive=False, range_str='') ->
        Perform a regular expression search.

            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            added           -   Search in the added text (i.e. italics).
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        info_print("Searching for regular expression '%s'..." % search_terms,
                   tag=1)

        # re.I is case insensitive.
        flags = re.I if not case_sensitive else 0

        try:
            # Make a regular expression from the search_terms.
            search_regx = re.compile(r'%s' % search_terms, flags)
        except Exception as err:
            print('There is a problem with the regular expression "%s": %s' % \
                    (search_terms, err), file=sys.stderr)
            exit()

        if range_str:
            # Only search through the supplied range.
            ref_iter = self._sorted_iter(range_str)
        else:
            # Search the entire Bible.
            ref_iter = VerseIter('Genesis 1:1')

        return self.find_from_regex(ref_iter, search_regx, strongs, morph,
                                    tag=1, try_clean=True)

    def find_from_regex(self, ref_iter, search_regex, strongs=False,
                        morph=False, added=True, tag=3, try_clean=False):
        """ Iterates through all the verses in the ref iter iterator and
        returns a list of verses whose text matches search_regx.

        """

        # Get an iterator that will return tuples
        # (verse_reference, verse_text).
        verse_iter = IndexedVerseTextIter(ref_iter, strongs=strongs,
                                          morph=morph, added=added,
                                          module=self._module_name)

        found_set = set()
        for verse_ref, verse_text in verse_iter:
            info_print('\033[%dD\033[KSearching...%s' % \
                       (len(verse_ref) + 20, verse_ref), end='', tag=tag)

            # Search for matches in the verse text.
            if search_regex.search(verse_text):
                found_set.add(verse_ref)
            elif try_clean and not strongs and not morph:
                # Should we do this or should we trust the user knows what
                # puctuation are in the verses?
                clean_verse_text = self._clean_text(verse_text)
                if search_regex.search(clean_verse_text):
                    found_set.add(verse_ref)

        info_print("...Done.", tag=tag)

        return found_set

    def mixed_search(self, search_terms, strongs=False, morph=False,
                     added=True, case_sensitive=False, range_str=''):
        """ mixed_search(self, search_terms, strongs=False, morph=False,
               case_sensitive=False, range_str='') ->
        Perform a mixed search.

            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            added           -   Search in the added text (i.e. italics).
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.

        """

        found_set = set()
        not_set = set()
        and_set = set()
        or_set = set()
        xor_set = set()

        combine_dict = {
                '!': not_set.update,
                '+': and_set.intersection_update,
                '|': or_set.update,
                '^': xor_set.symmetric_difference_update,
                }

        for term in search_terms:
            if term[0] in '!+^|':
                # Set the correct combining function, and cleanup the item.
                if term[0] == '+' and not and_set:
                    # All of these verses go in the output.
                    combine_func = and_set.update
                else:
                    combine_func = combine_dict[term[0]]
                term = term[1:]
            else:
                if self._multi and found_set:
                    # If multiword is default and found_set is not empty
                    # make all search terms appear in the output.
                    combine_func = found_set.intersection_update
                else:
                    # Any of these verses could be in the output
                    combine_func = found_set.update

            if term.startswith('&'):
                # Allow regular expression searching.
                term = term[1:]
                search_func = self.regex_search
            elif ' ' in term:
                # Search term is a quoted string, so treat it like a phrase.
                if term.startswith('~'):
                    # ~'s trigger ordered multiword or sloppy phrase search.
                    term = term[1:]
                    search_func = self.ordered_multiword_search
                else:
                    search_func = self.mixed_phrase_search
            elif '*' in term:
                # Search for partial words.
                search_func = self.partial_word_search
            else:
                # A single word should be (multi/any)-word.
                search_func = self.multiword_search

            # Perform a strongs search.
            strongs = bool(self._strongs_regx.match(term.upper()))
            # Perform a morpholagical search.
            morph = bool(self._morph_regx.match(term.upper()))

            # Search for words or phrases.
            temp_set = search_func(term, strongs, morph, added, case_sensitive,
                                   range_str)

            # Add the results to the correct set.
            combine_func(temp_set)

        # Update the result set.
        found_set.update(or_set)
        found_set.update(xor_set)

        if and_set and found_set:
            # Make sure all the verses that are in the output have the words
            # or phrases that hade a '+' in front of them.
            found_set = and_set.union(found_set.intersection(and_set))
        elif and_set:
            # Found set must be empty to fill it with and_set's contents.
            found_set.update(and_set)

        # Finally remove all the verses that are in the not_set.
        found_set.difference_update(not_set)

        return found_set

    def sword_search(self, search_terms, strongs=False, morph=False,
                     added=True, case_sensitive=False, range_str='',
                     search_type='lucene'):
        """ sword_search(self, search_terms, strongs=False, morph=False,
                case_sensitive=False, range_str='', search_type=-4) ->
        Use the sword module to search for the terms.

            search_terms    -   Terms to search for.
            strongs         -   Search for Strong's Number phrases.
            morph           -   Search for Morphological Tag phrases.
            case_sensitive  -   Perform a case sensitive search.
            range_str       -   A verse range to limit the search to.
            search_type     -   What search type to use.

        """

        search_terms = ' '.join(search_terms)

        info_print("Searching using the Sword library for "
                   "'%s'..." % search_terms, tag=1)

        found_set = set()

        search_type_dict = {
                'regex': 0,
                'phrase': -1,
                'multiword': -2,
                'entryattrib': -3,   # (e.g. Word//Lemma//G1234)
                'lucene': -4
                }

        try:
            # Render the text as plain.
            markup = Sword.MarkupFilterMgr(Sword.FMT_PLAIN)
            # Don't own this or it will crash.
            markup.thisown = False
            mgr = Sword.SWMgr(markup)
            # Load the module.
            module = mgr.getModule(self._module_name)

            # Set the search type based on the search_type argument.
            search_type = search_type_dict.get(search_type.lower(), -4)

            # Make sure we can search like this.
            if not module.isSearchSupported(search_terms, search_type):
                print("Search not supported", file=sys.stderr)
                return found_set()

            # Get the range key.
            if not range_str:
                range_str = 'Genesis-Revelation'
            range_k = Sword.VerseKey().parseVerseList(range_str, 'Genesis 1:1',
                                                      True)

            flags = re.I if not case_sensitive else 0

            if strongs:
                # Search for strongs numbers.
                # I don't know how to search for morphological tags using
                # Swords search function.
                prefix = 'lemma:'
                for term in ','.join(search_terms.split()).split(','):
                    if not term.startswith('lemma:'):
                        # Make the term start with lemma: so sword will find
                        # it.
                        term = '%s%s' % (prefix, term)
                    # Perform the search.
                    resource = module.doSearch(term, search_type, flags,
                                               range_k)
                    # Get the list of references from the range text.
                    found_set.update(resource.getRangeText().split('; '))
            else:
                # Perform the search.
                resource = module.doSearch(search_terms, search_type, flags,
                                           range_k)
                # Get the list of references from the range text.
                found_set.update(resource.getRangeText().strip().split('; '))
        except Exception as err:
            print("There was a problem while searching: %s" % err,
                  file=sys.stderr)

        found_set.discard('')

        return found_set

    @_process_search
    def test_search(self, search_terms, strongs=False, morph=False,
                    added=True, case_sensitive=False, range_str=''):
        """ A Test.

        """

        ref_set = self._index_dict.value_union(search_terms.split(),
                                                 case_sensitive)
        if range_str:
            # Only search through the supplied range.
            ref_set.intersection_update(range_str)

        ref_list = sorted(ref_set, key=sort_key)

        term_dict = defaultdict(list)
        raw_dict = RawDict(iter(ref_list), self._module_name)
        words_len = 0
        for verse_ref, (verse_text, verse_dict) in raw_dict:
            for term in search_terms.split():
                if self._strongs_regx.match(term):
                    num = self._strongs_regx.sub('\\1', term)
                    words = set(verse_dict[num.upper()])
                    if words:
                        term_dict[num.upper()].append({verse_ref: words})
                elif self._morph_regx.match(term):
                    tag = self._morph_regx.sub('\\1', term)
                    words = set(verse_dict[tag.upper()])
                    if words:
                        term_dict[tag.upper()].append({verse_ref: words})
                else:
                    for key, value in verse_dict['_words'][0].items():
                        if ' %s ' % term.lower() in ' %s ' % key.lower():
                            attr_dict = value[0]
                            if strongs and 'strongs' in attr_dict:
                                attr_list = attr_dict['strongs']
                                attr_list.append(key)
                                term_dict[term].append({verse_ref: attr_list})
                            if morph and 'morph' in attr_dict:
                                attr_list = attr_dict['morph']
                                attr_list.append(key)
                                words_len = max(len(attr_list), words_len)
                                term_dict[term].append({verse_ref: attr_list})
        len_longest_ref = len(max(ref_set, key=len))
        for key, value in term_dict.items():
            words_len = max([len(i) for d in value for i, v in d.items()])
            print('%s:' % key)
            for dic in value:
                ref, words = tuple(dic.items())[0]
                if isinstance(words, list):
                    w_str = '"%s"' % '", "'.join(words[:-1])
                    l_str = '"%s"' % words[-1]
                    words_str = '{0:{2}}: {1}'.format(w_str, l_str, words_len)
                else:
                    words_str = '"%s"' % '", "'.join(words)
                print('\t{0:{1}}: {2}'.format(ref, len_longest_ref, words_str))
                    #print('\t{0:{1}}: "{2}"'.format(ref, len_longest_ref,
                    #                                 '", "'.join(words)))
        exit()

    @_process_search
    def test2_search(self, search_terms, strongs=False, morph=False,
                     added=True, case_sensitive=False, range_str=''):
        """ A Test.

        """

        ref_set = self._index_dict.value_union(search_terms.split(),
                                               case_sensitive)
        if range_str:
            # Only search through the supplied range.
            ref_set.intersection_update(range_str)

        ref_iter = iter(sorted(ref_set, key=sort_key))
        # Get an iterator that will return tuples
        # (verse_reference, verse_text).
        verse_iter = IndexedVerseTextIter(ref_iter, strongs=True,
                                          morph=morph, added=added,
                                          module=self._module_name)

        # This will skip words.
        not_words_str = r'\b\w+\b'
        # This will skip Strong's Numbers.
        not_strongs_str = r'<[^>]*>'
        # This wil skip Morphological Tags.
        not_morph_str = r'\{[^\}]*\}'
        # This will skip all punctuation.  Skipping ()'s is a problem for
        # searching Morphological Tags, but it is necessary for the
        # parenthesized words.  May break highlighting.
        not_punct_str = r'[\s,\?\!\.;:\\/_\(\)\[\]"\'-]'
        max_ref_len = len(max(ref_set, key=len))
        found_set = set()
        term_dict = defaultdict(list)
        for verse_ref, verse_text in verse_iter:
            for term in search_terms.split():
                if self._strongs_regx.match(term):
                    test_regx = re.compile(r'''
                            \s
                            ((?:\b\w+\b|[\s,\?\!\.;:\\/_\(\)\[\]"\'-])+)
                            \s
                            ((?:%s)+)
                            ''' % term, re.I | re.X)
                elif self._morph_regx.match(term):
                    test_regx = re.compile(r'''
                            \s((?:\b\w+\b|[\s,\?\!\.;:\\/_\(\)\[\]"\'-])+)
                            (?:<[^>]*>|\s)+
                            ((?:%s)+)
                            ''' % term, re.I | re.X)
                else:
                    test_regx = re.compile(r'''
                            ((?:\b\w+\b|[\s,\?\!\.;:\\/_\(\)\[\]"\'-])*?
                            %s
                            (?:\b\w+\b|[\s,\?\!\.;:\\/_\(\)\[\]"\'-])+)+
                            ((?:<[^>]*>|\{[^\}]*\}|\s)+)
                            ''' % term, re.I | re.X)
                for match in test_regx.finditer(verse_text):
                    phrase, num = match.groups()
                    phrase = phrase.strip(',').strip('.').strip()
                    phrase = phrase.strip(';').strip('?').strip(':').strip()
                    num = num.replace('<', '').replace('>', '')
                    num = num.replace('{', '').replace('}', '')
                    if not phrase or not num.strip():
                        if not strongs:
                            break
                        print(verse_ref, verse_text)
                        print(match.group(), match.groups())
                        exit()
                    num = '"%s"' % '", "'.join(num.split())
                    term_dict[term].append(
                            '\t{0:{1}}: {2:{4}}: "{3}"'.format(verse_ref,
                                                               max_ref_len,
                                                               num, phrase,
                                                               18)
                                          )
        for term, lst in term_dict.items():
            term = term.replace('<', '').replace('>', '')
            term = term.replace('{', '').replace('}', '')
            print('%s:\n%s' % (term, '\n'.join(lst)))
        exit()

    @_process_search
    def test3_search(self, search_terms, strongs=False, morph=False,
                     added=True, case_sensitive=False, range_str=''):
        """ A Test.

        """

        ref_set = self._index_dict.value_union(search_terms.split(),
                                               case_sensitive)
        if range_str:
            # Only search through the supplied range.
            ref_set.intersection_update(range_str)

        if not ref_set:
            exit()

        ref_iter = iter(sorted(ref_set, key=sort_key))
        # Get an iterator that will return tuples
        # (verse_reference, verse_text).
        verse_iter = VerseTextIter(ref_iter, strongs=strongs,
                                   morph=morph, render='raw',
                                   module=self._module_name)

        found_set = set()
        strong_regx = re.compile(r'strong:([GH]\d+)', re.I)
        morph_regx = re.compile(r'(?:Morph|robinson):([\w-]*)', re.I)
        tag_regx = re.compile(r'''
                ([^<]*)                             # Before tag.
                <(?P<tag>q|w|transChange|note)      # Tag name.
                ([^>]*)>                            # Tag attributes.
                ([\w\W]*?)</(?P=tag)>               # Tag text and end.
                ([^<]*)                             # Between tags.
                ''', re.I | re.X)
        divname_regx = re.compile(r'''
                    (?:<seg>)?
                    <(?:divineName)>+
                    ([^<]*?)
                    ([\'s]*)
                    </(?:divineName)>
                    (?:</seg>)?
                    ''', re.I | re.X)
        xadded_regx = re.compile(r'<seg subType="x-added"[^>]*>([^<]*)</seg>',
                                 re.I)
        div_upper = lambda m: m.group(1).upper() + m.group(2)
        marker_regx = re.compile(r'.*marker="(.)".*', re.I)
        term_dict = defaultdict(list)
        len_attrs = 0

        for verse_ref, verse_text in verse_iter:
            #print(render_raw(verse_text, strongs, morph))
            #print(render_raw2(verse_text, strongs, morph))
            #continue
            for term in search_terms.split():
                term = term.replace('<', '').replace('>', '')
                term = term.replace('{', '').replace('}', '')
                v_text = ''
                info_print('%s\n' % verse_text, tag=4)
                term_regx = re.compile('\\b%s\\b' % term, re.I)
                for match in tag_regx.finditer(verse_text):
                    opt, tag_name, tag_attr, tag_text, punct = match.groups()
                    tag_text = xadded_regx.sub('\\1', tag_text)
                    if match.re.search(tag_text):
                        match_list = match.re.findall(tag_text + punct)
                    else:
                        match_list = [match.groups()]
                    for tag_tup in match_list:
                        opt, tag_name, tag_attr, tag_text, punct = tag_tup
                        info_print(tag_tup, tag=4)
                        value_list = []
                        attr_list = []
                        strongs_list = []
                        morph_list = []
                        tag_text = divname_regx.sub(div_upper, tag_text)
                        v_text += marker_regx.sub('\\1 ', opt) + tag_text + \
                                                                 punct
                        if term.upper() in tag_attr:
                            attr_list = [term.upper()]
                        elif term_regx.search(tag_text):
                            if strongs or not morph:
                                strongs_list = strong_regx.findall(tag_attr)
                            if morph:
                                morph_list = morph_regx.findall(tag_attr)

                        for lst in (strongs_list, morph_list, attr_list):
                            if lst:
                                attr_str = '%s"' % '", "'.join(lst)
                                value_list = [attr_str, tag_text.strip()]
                                term_dict[term].append({verse_ref: value_list})
                                len_attrs = max(len(attr_str), len_attrs)
                info_print(v_text, tag=4)
        max_len_ref = len(max(ref_set, key=len))
        for term, lst in term_dict.items():
            print('%s:' % term)
            for dic in lst:
                ref, (attrs, s) = list(dic.items())[0]
                s_l = '{1:{0}}: "{2}'.format(len_attrs, attrs, s)
                print('\t{0:{1}}: "{2}"'.format(ref, max_len_ref, s_l))

        exit()

    @_process_search
    def test4_search(self, search_terms, strongs=False, morph=False,
                     added=True, case_sensitive=False, range_str=''):
        """ A Test.

        """

        ref_set = self._index_dict.value_union(search_terms.split(),
                                               case_sensitive)
        if range_str:
            # Only search through the supplied range.
            ref_set.intersection_update(range_str)

        if not ref_set:
            exit()

        ref_iter = iter(sorted(ref_set, key=sort_key))
        # Get an iterator that will return tuples
        # (verse_reference, verse_text).
        verse_iter = VerseTextIter(ref_iter, strongs=strongs,
                                   morph=morph, render='raw',
                                   module=self._module_name)

        found_set = set()
        strong_regx = re.compile(r'strong:([GH]\d+)', re.I)
        morph_regx = re.compile(r'(?:Morph|robinson):([\w-]*)', re.I)
        tag_regx = re.compile(r'''
                ([^<>]*)                                # Before tag.
                <(?P<tag>seg|q|w|transChange|note|title)# Tag name.
                ([^>]*)>                                # Tag attributes.
                ([\w\W]*?)</(?P=tag)>                   # Tag text and end.
                ([^<]*)                                 # Between tags.
                ''', re.I | re.X)
        divname_regx = re.compile(r'''
                    <(?:divineName)>
                    ([^<]*?)
                    ([\'s]*)
                    </(?:divineName)>
                    ''', re.I | re.X)
        div_upper = lambda m: m.group(1).upper() + m.group(2)
        marker_regx = re.compile(r'.*marker="(.)".*', re.I)
        term_dict = defaultdict(list)
        len_attrs = 0

        def recurse_tag(text, term, verse_ref, ctag_attr=''):
            """ Recursively parses raw verse text using regular expressions,
            and a list of dictionaries of the search term and any attributes
            with its text.

            """

            term_list = []
            for match in tag_regx.finditer(text):
                value_list = []
                attr_list = []
                strongs_list = []
                morph_list = []
                opt, tag_name, tag_attr, tag_text, punct = match.groups()
                if match.re.search(tag_text):
                    term_list.extend(recurse_tag(tag_text, term, verse_ref,
                                                 tag_attr))
                else:
                    info_print((opt, tag_name, tag_attr, tag_text, punct),
                               tag=4)
                    if marker_regx.match(opt):
                        opt = ''
                    tag_text = opt + divname_regx.sub(div_upper,
                                                      tag_text) + punct
                    if term.upper() in tag_attr or term.upper() in ctag_attr:
                        attr_list = [term.upper()]
                    elif term_regx.search(tag_text):
                        if strongs or not morph:
                            strongs_list.extend(strong_regx.findall(tag_attr))
                            strongs_list.extend(strong_regx.findall(ctag_attr))
                        if morph:
                            morph_list.extend(morph_regx.findall(tag_attr))
                            morph_list.extend(morph_regx.findall(ctag_attr))
                    for lst in (strongs_list, morph_list, attr_list):
                        if lst:
                            a_str = '%s"' % '", "'.join(lst)
                            value_list = [a_str, tag_text.strip()]
                            term_list.append({verse_ref: value_list})
            return term_list

        for verse_ref, verse_text in verse_iter:
            #print(render_raw(verse_text, strongs, morph))
            #print(render_raw2(verse_text, strongs, morph))
            #continue
            for term in search_terms.split():
                term = term.replace('<', '').replace('>', '')
                term = term.replace('{', '').replace('}', '')
                v_text = ''
                info_print('%s\n' % verse_text, tag=4)
                term_regx = re.compile('\\b%s\\b' % term, re.I)
                value_list = recurse_tag(verse_text, term, verse_ref)
                if value_list:
                    for i in value_list:
                        len_attrs = max(len(i[verse_ref][0]), len_attrs)
                    term_dict[term].extend(value_list)

        max_len_ref = len(max(ref_set, key=len))
        for term, lst in term_dict.items():
            print('%s:' % term)
            for dic in lst:
                ref, (attrs, s) = list(dic.items())[0]
                s_l = '{1:{0}}: "{2}'.format(len_attrs, attrs, s)
                print('\t{0:{1}}: "{2}"'.format(ref, max_len_ref, s_l))

        return set()

    concordance_search = test4_search


class SearchCmd(Cmd):
    """ A Command line interface for searching the Bible.

    """

    def __init__(self, module='KJV'):
        """ Initialize the settings.

        """

        self.prompt = '\001[33m\002search\001[m\002> '
        self.intro = '''
    %s  Copyright (C) 2011  Josiah Gordon <josiahg@gmail.com>
    This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
    This is free software, and you are welcome to redistribute it
    under certain conditions; type `show c' for details.

        This is a Bible search program that searches the KJV
        sword module.  If you need help type 'help' to display a list of valid
        commands.  For help on a specific command type 'help <command>.'

        Examples:

        mixed 'jordan h03383'   (Finds all verses with Strong's number 'H03383'
                                 translated 'Jordan')

        concordance live        (Lists the references of all the verses with
                                 the word 'live' in them, the Strong's number
                                 that was used, and what the phrase is that
                                 that Strong's number is translated as.)

        concordance h02418      (Lists the references of all the verses with
                                 the Strong's number 'H02418' and how it was
                                 translated.  It only occures six times and all
                                 of them are in Daniel.)

        strongs h02418          (Looks up and gives the definition of the
                                 Strong's number 'H02418.')

        set range gen-mal       (Sets the range to the Old Testament.)

        Just about everything has tab-completion, so you can hit tab a couple
        of times to see all the completions to what you are typing.

        If you want to see this intro again type: 'intro'

        To find out more type 'help'

        (example: 'help search' will list the help for the search command.)

        To exit type 'quit' or hit 'CTRL+D'

        ''' % os.path.basename(argv[0])
        super(SearchCmd, self).__init__()
        self._quoted_regex = re.compile('''
                            ((?P<quote>'|")
                            .*?
                            (?P=quote)|[^'"]*)
                            ''', re.X)

        # Perform the specified search.
        self._search = Search(module=module)
        self._results = set()
        self._search_list = []
        self._highlight_list = []
        self._words = self._search._index_dict['_words_']
        self._strongs = self._search._index_dict['_strongs_']
        self._morph = self._search._index_dict['_morph_']
        self._book_list = list(book_gen())
        self._setting_dict = {
                'search_type': 'mixed',
                'search_strongs': False,
                'search_morph': False,
                'case_sensitive': False,
                'context': 0,
                'one_line': False,
                'show_notes': False,
                'show_strongs': False,
                'show_morph': False,
                'added': True,
                'range': '',
                'extras': (),
                'module': module,
                }
        self._search_types = ['mixed', 'mixed_phrase', 'multiword', 'anyword',
                              'combined', 'partial_word', 'ordered_multiword',
                              'regex', 'eitheror', 'sword_lucene',
                              'sword_phrase', 'sword_multiword',
                              'sword_entryattrib']

    def _complete(self, text, line, begidx, endidx, complete_list):
        """ Return a list of matching text.

        """

        retlist = [i for i in complete_list if i.startswith(text)]
        if not retlist:
            # If nothing was found try words that contain the text.
            retlist = [i for i in complete_list if text in i]
        if not retlist:
            # Finally try matching misspelled words.
            retlist = get_close_matches(text, complete_list, cutoff=0.7)
        return retlist

    def _get_list(self, args):
        """ Split the args into quoted strings and seperate words.

        """

        arg_list = []

        # Split the arg string into quoted phrases and single words.
        for i, c in self._quoted_regex.findall(args):
            if c in ['"', "'"]:
                arg_list.append(i.strip(c))
            else:
                arg_list.extend(i.split())

        return arg_list

    def do_test(self, args):
        """ A Test.

        """

        quoted_regex = re.compile('''((?P<quote>'|").*?(?P=quote)|[^'"]*)''')
        print(quoted_regex.findall(args))
        print(self._get_list(args))

    def _print(self, text_iter):
        """ Print all the text breaking it and screens so the user can read it
        all.

        """

        count = 0
        for verse in text_iter:
            count += len(verse.splitlines()) if '\n' in verse else 1
            print(verse)
            if count >= screen_size()[0] - 4:
                count = 0
                try:
                    input('[Press enter to see more, or CTRL+D to end.]')
                    print('[1A[K', end='')
                except:
                    print('[G[K', end='')
                    break

    def precmd(self, line):
        """ Set the correct settings before running the line.

        """

        if not line:
            return line

        cmd = line.split()[0]
        if cmd in self._search_types:
            search_type = cmd
            if search_type.startswith('sword_'):
                self._setting_dict['extras'] = (search_type[6:],)
                search_type = search_type[:5]
            else:
                self._setting_dict['extras'] = ()
            self._setting_dict['search_type'] = search_type
        return line

    def postcmd(self, stop, line):
        """ If lookup was called then show the results.

        """

        if not line:
            return stop

        cmd = line.split()[0]
        if cmd == 'lookup':
            self.onecmd('show_results')
        return stop

    def completedefault(self, text, line, begidx, endidx):
        """ By default complete words in the Bible.

        """

        words_list = self._words
        return self._complete(text, line, begidx, endidx, words_list)

    def do_shell(self, args):
        """ Execute shell commands.

        """

        os.system(args)

    def do_concordance(self, args):
        """ Perform a concordance like search.

        """

        if not args:
            return

        arg_list = self._get_list(args)

        # Search.
        strongs_search = self._setting_dict['search_strongs']
        morph_search = self._setting_dict['search_morph']
        search_range = self._setting_dict['range']
        case_sensitive = self._setting_dict['case_sensitive']
        search_added = self._setting_dict['added']
        self._search.test4_search(arg_list, strongs_search, morph_search,
                                  search_added, case_sensitive, search_range)

    def do_show(self, args):
        """ Show relevent parts of the GPL.

        """

        if args.lower() in ['c', 'copying']:
            # Show the conditions.
            print(copying_str)
        elif args.lower() in ['w', 'warranty']:
            # Show the warranty.
            print(warranty_str)
        else:
            # Show the entire license.
            print('%s%s' % (copying_str, warranty_str))

    def do_EOF(self, args):
        """ Exit when eof is recieved.

        """

        return True

    def do_quit(self, args):
        """ Exit.

        """

        return True

    def do_help(self, args):
        """ Print the help.

        """

        if args:
            try:
                self._print(getattr(self, 'do_%s' % args).__doc__.splitlines())
                return
            except:
                pass
        super(SearchCmd, self).do_help(args)

    def do_intro(self, args):
        """ Re-print the intro screen.

        """

        self._print(self.intro.splitlines())

    def complete_show_results(self, text, line, begidx, endidx):
        """ Tab completion for the show_results command.

        """

        cmd_list = ['strongs', 'morph', 'notes', 'one_line']
        return self._complete(text, line, begidx, endidx, cmd_list)

    def do_show_results(self, args):
        """ Output the results.

        Print out all the verses that were either found by searching or by
        lookup.

        Extra arguments:
            +/-strongs      -   Enable/disable strongs in the output.
            +/-morph        -   Enable/disable morphology in the output
            +/-notes        -   Enable/disable foot notes in the output.
            +/-added        -   Enable/disable added text in the output.
            +/-one_line     -   Enable/disable one line output.
            anything else   -   If the output is from looking up verses with
                                the lookup command, then any other words or
                                quoted phrases given as arguments will be
                                highlighted in the output.

        """

        search_type = self._setting_dict['search_type']
        strongs_search = self._setting_dict['search_strongs']
        morph_search = self._setting_dict['search_morph']
        search_range = self._setting_dict['range']
        case_sensitive = self._setting_dict['case_sensitive']
        search_added = self._setting_dict['added']
        module_name = self._setting_dict['module']
        highlight_list = self._highlight_list
        kwargs = self._setting_dict
        results = self._results

        # Get the output arguments.
        show_strongs = self._setting_dict['show_strongs'] or strongs_search
        show_morph = self._setting_dict['show_morph'] or morph_search
        show_notes = self._setting_dict['show_notes']
        one_line = self._setting_dict['one_line']

        arg_list = self._get_list(args)

        if '+strongs' in arg_list:
            show_strongs = True
            arg_list.remove('+strongs')
        if '+morph' in args:
            show_morph = True
            arg_list.remove('+morph')
        if '-strongs' in args:
            show_strongs = False
            arg_list.remove('-strongs')
        if '-morph' in args:
            show_strongs = False
            arg_list.remove('-morph')
        if '+notes' in args:
            show_notes = True
            arg_list.remove('+notes')
        if '-notes' in args:
            show_notes = False
            arg_list.remove('-notes')
        if '+one_line' in args:
            one_line = True
            arg_list.remove('+one_line')
        if '-one_line' in args:
            one_line = False
            arg_list.remove('-one_line')
        if '+added' in args:
            search_added = True
            arg_list.remove('+added')
        if '-added' in args:
            search_added = False
            arg_list.remove('-added')

        if search_range:
            results.intersection_update(parse_verse_range(search_range))

        if not highlight_list:
            # Highlight anything else the user typed in.
            highlight_list = arg_list

        # Don't modify regular expression searches.
        if search_type != 'regex':
            regx_list = build_highlight_regx(highlight_list, case_sensitive,
                        (search_type == 'ordered_multiword'))
            if kwargs['context']:
                regx_list.extend(build_highlight_regx(results, case_sensitive))
        else:
            arg_str = ' '.join(arg_list)
            regx_list = [re.compile(arg_str, re.I if case_sensitive else 0)]

        # Flags for the highlight string.
        flags = re.I if not case_sensitive else 0
        # Add the specified number of verses before and after to provide
        # context.
        context_results = sorted(add_context(results, kwargs['context']),
                                 key=sort_key)
        # Get a formated verse string generator.
        verse_gen = render_verses_with_italics(context_results,
                                               not one_line,
                                               show_strongs, show_morph,
                                               search_added,
                                               show_notes,
                                               highlight_search_terms,
                                               module_name, regx_list,
                                               highlight_text, flags)
        if one_line:
            # Print it all on one line.
            print('  '.join(verse_gen))
        else:
            # Print the verses on seperate lines.
            self._print(verse_gen)
            #print('\n'.join(verse_gen))

    def complete_lookup(self, text, line, begidx, endidx):
        """ Try to complete Verse references.

        """

        name_list = self._book_list
        text = text.capitalize()
        return self._complete(text, line, begidx, endidx, name_list)

    def do_lookup(self, args):
        """ Lookup the verses by references.

        Example:    lookup gen1:3-5;mal3    (Look up Genesis chapter 1 verses
                                            3-5 and Malachi chapter 3.)

        """

        self._results = parse_verse_range(args)
        self._highlight_list = []

    def complete_strongs(self, text, line, begidx, endidx):
        """ Tabe complete Strong's numbers.

        """
        text = text.capitalize()
        return self._complete(text, line, begidx, endidx, self._strongs)

    def do_strongs(self, numbers):
        """ Lookup one or more Strong's Numbers.

        strongs number,number,number....

        """

        # Lookup all the Strong's Numbers in the argument list.
        # Make all the numbers seperated by a comma.
        strongs_list = ','.join(numbers.upper().split()).split(',')
        #TODO: Find what Strong's Modules are available and use the best,
        #      or let the user decide.
        greek_strongs_lookup = Lookup('StrongsRealGreek')
        hebrew_strongs_lookup = Lookup('StrongsRealHebrew')
        for strongs_num in strongs_list:
            # Greek Strong's Numbers start with a 'G' and Hebrew ones start
            # with an 'H.'
            if strongs_num.upper().startswith('G'):
                mod_name = 'StrongsRealGreek'
            else:
                mod_name = 'StrongsRealHebrew'
            print('%s\n' % mod_lookup(mod_name, strongs_num[1:]))

    def complete_morph(self, text, line, begidx, endidx):
        """ Tabe complete Morphological Tags.

        """
        text = text.capitalize()
        return self._complete(text, line, begidx, endidx, self._morph)

    def do_morph(self, tags):
        """ Lookup one or more Morphological Tags.

        morph tag,tag,tag....

        """

        # Lookup all the Morphological Tags in the argument list.
        # I don't know how to lookup Hebrew morphological tags, so I
        # only lookup Greek ones in 'Robinson.'
        print('%s\n' % mod_lookup('Robinson', tags.upper()))

    def do_websters(self, words):
        """ Lookup one or more words in Websters Dictionary.

        websters word,word,word...

        """

        # Lookup words in the dictionary.
        print('%s\n' % mod_lookup('WebstersDict', words))

    def do_kjvd(self, words):
        """ Lookup one or more words in the KJV Dictionary.

        kjvd word,word,word...

        """

        # Lookup words in the KJV dictionary.
        print('%s\n' % mod_lookup('KJVD', words))

    def do_daily(self, daily):
        """ Display a daily devotional from 'Bagsters Daily light.'

        daily date/today

        Dates are given in the format Month.Day.  The word 'today' is an alias
        to today's date.  The default is to lookup today's devotional.

        """

        daily = 'today' if not daily else daily

        # Lookup the specified daily devotional.
        if daily.lower() == 'today':
            # Today is an alias for today's date.
            daily = strftime('%m.%d')
        daily_lookup = Lookup('Daily')
        # Try to make the output nicer.
        print(daily_lookup.get_formatted_text(daily))

    def complete_set(self, text, line, begidx, endidx):
        """ Complete setting options.

        """

        setting_list = self._setting_dict.keys()
        return self._complete(text, line, begidx, endidx, setting_list)

    def do_set(self, args):
        """ Set settings.

        Run without arguments to see the current settings.

        set show_strongs = True/False   -   Enable strongs numbers in the
                                            output.
        set show_morph = True/False     -   Enable morphology in the output.
        set context = <number>          -   Show <number> verses of context.
        set case_sensitive = True/False -   Set the search to case sensitive.
        set range = <range>             -   Confine search/output to <range>.
        set one_line = True/False       -   Don't break output at verses.
        set added = True/False          -   Show/search added text.
        set show_notes = True/False     -   Show foot-notes in output.
        set search_type = <type>        -   Use <type> for searching.
        set search_strongs = True/False -   Search Strong's numbers
                                            (deprecated).
        set search_morph = True/False   -   Search Morphological Tags
                                            (deprecated).

        """

        if not args:
            print("Current settings:\n")
            max_len = len(max(self._setting_dict.keys(), key=len))
            for setting, value in self._setting_dict.items():
                if setting.lower() == 'range':
                    if not Sword:
                        value = VerseRange.parse_range(value)
                        value = '; '.join(str(i) for i in value)
                    else:
                        key = Sword.VerseKey()
                        range_list = key.parseVerseList(value, 'Genesis 1:1',
                                                        True, False)
                        value = range_list.getRangeText()
                print('{1:{0}} = {2}'.format(max_len, setting, value))
            print()
        else:
            for setting in args.split(';'):
                if '=' in setting:
                    k, v = setting.split('=')
                elif ' ' in setting:
                    k, v = setting.split()
                else:
                    print(self._setting_dict.get(setting, ''))
                    continue
                k = k.strip()
                v = v.strip()
                if isinstance(v, str):
                    if v.lower() == 'false':
                        v = False
                    elif v.lower() == 'true':
                        v = True
                    elif v.isdigit():
                        v = int(v)
                self._setting_dict[k] = v

    def complete_search(self, text, line, begidx, endidx):
        """ Bible word completion to make searching easier.

        """

        words_list = self._words
        return self._complete(text, line, begidx, endidx, words_list)

    complete_mixed = complete_search
    complete_mixed_phrase = complete_search
    complete_multiword = complete_search
    complete_anyword = complete_search
    complete_combined = complete_search
    complete_partial_word = complete_search
    complete_ordered_multiword = complete_search
    complete_regex = complete_search
    complete_eitheror = complete_search
    complete_sword_lucene = complete_search
    complete_sword_phrase = complete_search
    complete_sword_multiword = complete_search
    complete_sword_entryattrib = complete_search

    def do_search(self, args):
        """ Search the Bible.

        Search types are:

            mixed               -   A search made up of a mix of most of the
                                    other search types.  Put an '!' in front of
                                    words/phrases that you don't want in any of
                                    the results.
            mixed_phrase        -   A phrase search that can include words,
                                    Strong's, and Morphology.  Can be used in
                                    the mixed search by including words in
                                    quotes.
            multiword           -   Search for verses containing each word at
                                    least once.  Use in the mixed search by
                                    putting a '+' in front of any word/phrase
                                    you want to be in all the results.
            anyword             -   Search for verses containing one or more of
                                    any of the words.  Use in the mixed search
                                    by putting a '|' in front of any
                                    word/phrase you want in any but not
                                    necessarily all the results.
            eitheror            -   Search for verses containing one and only
                                    one of the words.  In the mixed search put
                                    a '^' in front of two or more words/phrases
                                    to make the results contain one and only
                                    one of the marked search terms.
            combined            -   Search using a phrase like ('in' AND ('the'
                                    OR 'it')) finding verses that have both
                                    'in' and 'the' or both 'in' and 'it'.
                                    To do the same thing with the mixed search
                                    use a phrase like this:
                                    (mixed '+in' '^the' '^it').
            partial_word        -   Search for partial words (e.g. a search for
                                    'begin*' would find all the words starting
                                    with 'begin'.)  Use in the mixed search to
                                    make partial words in a phrase.
            ordered_multiword   -   Search for words in order, but not
                                    necessarily in a phrase.  In the mixed
                                    search put a '~' in front of any quoted
                                    group of words you want to be in that
                                    order, but you don't mind if they have
                                    other words between them.
            regex               -   A regular expression search (slow).


        Examples:

            mixed               -   (mixed '+~in the beg*' '!was') finds any
                                    verse that has the words 'in', 'the', and
                                    any word starting with 'beg', in order, but
                                    not the word 'was.'
            mixed_phrase        -   (mixed_phrase 'h011121 of gomer') finds any
                                    verse with that phrase.

            mixed search flags first column prefix (these should come first):
            ----------------------------------------------------------------
            ! = not (not in any of the results)
            + = all (in all the results)
            | = or  (in at least one result)
            ^ = exclusive or (only one in any of the results)

            not example: (mixed 'in the beginning' !was) results will have the
                         phrase 'in the beginning' but will not have the word
                         'was.'
            all example: (mixed 'in the beginning' +was) results may have the
                         phrase 'in the beginning' but all of them will have
                         the word 'was.' (note. this will find all verses with
                         the word 'was' in them if you want it to have the
                         phrase 'in the beginning' also you have to prefix it
                         with a '+' aswell)
            or example: (mixed 'in the beginning' |was) results will be all the
                        verses with the phrase 'in the beginning' and all the
                        verses with the word 'was.'  This is the default way
                        the mixed search operates, so the '|' can be excluded
                        in this case.
            exclusive or example: (mixed '^in the beginning' '^was') results
                                  will either have the phrase 'in the
                                  beginning' or the word 'was', but not both.
                                  To be effective you must have at least two
                                  search terms prefixed with '^.'

            mixed search flags second column prefix (these come after the first
            column flags):
            -------------------------------------------------------------------
            ~ = sloppy phrase or ordered multiword
            & = regular expression search.

            sloppy phrase example: (mixed '~in the beginning') results will
                                   have all the words 'in', 'the', and
                                   'beginning,' but they may have other words
                                   between them.
            regular expression example:
            (mixed '&\\b[iI]n\\b\s+\\b[tT[Hh][eE]\\b\s+\\b[bB]eginning\\b')
            results will be all the verses with the phrase 'in the beginning.'

        """

        if not args:
            return

        arg_list = self._get_list(args)
        arg_str = ' '.join(arg_list)
        self._search_list = arg_list

        extras = self._setting_dict['extras']
        search_type = self._setting_dict['search_type']

        try:
            # Get the search function asked for.
            search_func = getattr(self._search, '%s_search' % search_type)
        except AttributeError as err:
            # An invalid search type was specified.
            print("Invalid search type: %s" % search_type, file=sys.stderr)
            exit()

        # Search.
        strongs_search = self._setting_dict['search_strongs']
        morph_search = self._setting_dict['search_morph']
        search_range = self._setting_dict['range']
        case_sensitive = self._setting_dict['case_sensitive']
        search_added = self._setting_dict['added']
        self._results = search_func(arg_list, strongs_search, morph_search,
                                    search_added, case_sensitive, search_range,
                                    *extras)
        count = len(self._results)
        info_print("\nFound %s verse%s.\n" % \
                   (count, 's' if count != 1 else ''),
                   tag=-10)
        print("To view the verses type 'show_results.'")

        if search_type in ['combined', 'combined_phrase']:
            # Combined searches are complicated.
            # Parse the search argument and build a highlight string from the
            # result.
            arg_parser = CombinedParse(arg_str)
            parsed_args = arg_parser.word_list
            not_l = arg_parser.not_list
            # Remove any stray '+'s.
            #highlight_str = highlight_str.replace('|+', ' ')
            if search_type == 'combined_phrase':
                # A phrase search needs to highlight phrases.
                highlight_list = parsed_args
            else:
                highlight_list = ' '.join(parsed_args).split()
        # Build the highlight string for the other searches.
        elif search_type in ['anyword', 'multiword', 'eitheror',
                             'partial_word']:
            # Highlight each word separately.
            highlight_list = arg_str.split()
        elif search_type == 'mixed':
            # In mixed search phrases are in quotes so the arg_list should be
            # what we want, but don't include any !'ed words.
            highlight_list = [i for i in arg_list if not i.startswith('!')]
        elif search_type in ['phrase', 'mixed_phrase', 'ordered_multiword']:
            # Phrases should highlight phrases.
            highlight_list = [arg_str]
        elif search_type == 'sword':
            highlight_list = arg_list

        self._highlight_list = highlight_list

    do_mixed = do_search
    do_mixed_phrase = do_search
    do_multiword = do_search
    do_anyword = do_search
    do_combined = do_search
    do_partial_word = do_search
    do_ordered_multiword = do_search
    do_regex = do_search
    do_eitheror = do_search
    do_sword_lucene = do_search
    do_sword_phrase = do_search
    do_sword_multiword = do_search
    do_sword_entryattrib = do_search
